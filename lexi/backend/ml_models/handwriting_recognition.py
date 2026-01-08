import os
from typing import Dict, List, Any
from PIL import Image
from config import settings

class TesseractOCRProcessor:
    """Enhanced OCR with character analysis"""
    
    def __init__(self):
        self.tesseract_available = False
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.tesseract_available = True
        except ImportError:
            print("Tesseract not available")

    async def recognize_handwriting(self, image_path: str, language: str = "en") -> Dict[str, Any]:
        """Recognize handwriting with content validation"""
        # Input validation
        if not image_path or not isinstance(image_path, str):
            return {
                "success": False,
                "error": "Invalid image path",
                "recognized_text": "",
                "confidence": 0.0,
                "character_analysis": {"characters": []}
            }
        
        if not self.tesseract_available:
            return {
                "success": False,
                "error": "Tesseract not available - install with: pip install pytesseract",
                "recognized_text": "",
                "confidence": 0.0,
                "character_analysis": {"characters": []}
            }
        
        try:
            # Verify image exists and is readable
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}",
                    "recognized_text": "",
                    "confidence": 0.0,
                    "character_analysis": {"characters": []}
                }
            
            if not language or not isinstance(language, str):
                language = "en"
            
            image = Image.open(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Could not load image - invalid or corrupted file",
                    "recognized_text": "",
                    "confidence": 0.0,
                    "character_analysis": {"characters": []}
                }
            
            # VALIDATE IMAGE CONTENT FIRST
            content_validation = self._validate_image_content(image)
            if not content_validation["is_handwriting"]:
                return {
                    "success": False,
                    "error": content_validation["message"],
                    "recognized_text": "",
                    "confidence": 0.0,
                    "character_analysis": {"characters": []},
                    "content_type": content_validation["detected_type"]
                }
            
            # Perform OCR with per-word tokens
            ocr_result = self._ocr_with_tokens(image, language)
            text = ocr_result.get("text", "")
            tokens = ocr_result.get("tokens", [])
            
            # Always run character analysis even if OCR fails
            character_analysis = self._analyze_characters(image_path)
            
            # Map characters to words for actionable feedback
            mapping = self._map_characters_to_words(character_analysis.get("characters", []), tokens)
            word_feedback = self._build_word_feedback(tokens, mapping)
            
            # Post-process text if we got any
            if text:
                text = self._post_process_text(text)
            
            # Try to generate an overlay that shows words and character issues
            visual_overlay_path = ""
            try:
                visual_overlay_path = self._generate_visual_overlay_with_words(
                    image_path,
                    character_analysis,
                    tokens,
                    word_feedback
                )
            except Exception:
                # Fallback to previous overlay
                visual_overlay_path = character_analysis.get("visual_overlay_path", "")
            
            # Build a basic summary
            lines_estimated = max((t.get("line_num", 1) for t in tokens), default=1)
            content_summary = {
                "content_type": "handwriting",
                "lines_estimated": int(lines_estimated),
                "text_summary": text[:120]
            }
            
            return {
                "success": True,
                "recognized_text": text,
                "confidence": self._estimate_confidence(text),
                "errors": self._analyze_basic_errors(text),
                "image_analysis": self._analyze_image_quality(image),
                "character_analysis": character_analysis,
                "tokens": tokens,
                "word_feedback": word_feedback,
                "summary": content_summary,
                "visual_overlay_path": visual_overlay_path
            }
            
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "character_analysis": {"characters": []},
                "recognized_text": "",
                "confidence": 0.0
            }
    
    def _validate_image_content(self, image: Image.Image) -> Dict[str, Any]:
        """Validate that image contains handwriting, not humans or other content"""
        try:
            import cv2
            import numpy as np
            
            # Convert PIL to OpenCV format
            img_array = np.array(image.convert('RGB'))
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Check for human features (face detection)
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    return {
                        "is_handwriting": False,
                        "detected_type": "human_face",
                        "message": "I can see a person in this image. Please upload an image of handwritten text instead."
                    }
            except:
                pass  # Face detection failed, continue with other checks
            
            # Check image characteristics for handwriting
            height, width = gray.shape
            
            # Check if image is too small for meaningful handwriting
            if width < 100 or height < 50:
                return {
                    "is_handwriting": False,
                    "detected_type": "too_small",
                    "message": "Image is too small. Please upload a clearer image of your handwriting."
                }
            
            # Analyze color distribution
            color_std = np.std(gray)
            if color_std < 10:  # Very uniform color (likely blank or solid color)
                return {
                    "is_handwriting": False,
                    "detected_type": "uniform_color",
                    "message": "I don't see any handwriting in this image. Please make sure there's clear text written on paper."
                }
            
            # Check for text-like patterns using edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # Too many edges might indicate complex scenes (photos of people/objects)
            if edge_density > 0.3:
                return {
                    "is_handwriting": False,
                    "detected_type": "complex_scene",
                    "message": "This looks like a photo rather than handwriting. Please upload an image of text written on paper."
                }
            
            # Too few edges might indicate blank page or very faint writing
            if edge_density < 0.01:
                return {
                    "is_handwriting": False,
                    "detected_type": "no_content",
                    "message": "I don't see any clear handwriting. Please write with darker ink and ensure good lighting."
                }
            
            # Check for skin-like colors (indicates human in photo)
            hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_ratio = np.sum(skin_mask > 0) / (width * height)
            
            if skin_ratio > 0.15:  # More than 15% skin-colored pixels
                return {
                    "is_handwriting": False,
                    "detected_type": "human_detected",
                    "message": "I can see a person in this image. Please upload an image of handwritten text on paper instead."
                }
            
            # If we get here, it's likely handwriting
            return {
                "is_handwriting": True,
                "detected_type": "handwriting",
                "message": "Image appears to contain handwriting"
            }
            
        except Exception as e:
            # If validation fails, allow processing but with warning
            return {
                "is_handwriting": True,
                "detected_type": "unknown",
                "message": f"Could not validate image content: {str(e)}"
            }

    def _try_multiple_ocr_configs(self, image: Image.Image, language: str) -> str:
        """Try multiple OCR configurations to improve recognition"""
        configs = [
            '--psm 6 --oem 3',  # Uniform block of text
            '--psm 8 --oem 3',  # Single word
            '--psm 7 --oem 3',  # Single text line
            '--psm 13 --oem 3', # Raw line
            '--psm 3 --oem 3'   # Fully automatic
        ]
        
        best_text = ""
        best_confidence = 0
        
        # Try original and processed images
        images_to_try = [
            image,
            self._preprocess_image(image),
            self._preprocess_aggressive(image)
        ]
        
        for img in images_to_try:
            for config in configs:
                try:
                    text = self.pytesseract.image_to_string(
                        img, 
                        lang=language,
                        config=config
                    ).strip()
                    
                    if text and len(text) > len(best_text):
                        best_text = text
                        
                except Exception:
                    continue
        
        return best_text

    def _ocr_with_tokens(self, image: Image.Image, language: str) -> Dict[str, Any]:
        """Run OCR across multiple configs and return best text with per-word tokens."""
        if not self.tesseract_available:
            return {"text": "", "tokens": [], "mean_conf": 0.0}
        
        configs = [
            '--psm 6 --oem 3',  # Uniform block of text
            '--psm 7 --oem 3',  # Single line
            '--psm 8 --oem 3',  # Single word
            '--psm 3 --oem 3',  # Auto
            '--psm 13 --oem 3', # Raw line
        ]
        
        images_to_try = [
            image,
            self._preprocess_image(image),
            self._preprocess_aggressive(image)
        ]
        
        best = {"text": "", "tokens": [], "mean_conf": 0.0, "score": -1.0}
        
        for img in images_to_try:
            for config in configs:
                try:
                    data = self.pytesseract.image_to_data(
                        img,
                        lang=language,
                        config=config,
                        output_type=self.pytesseract.Output.DICT
                    )
                    tokens = []
                    for i in range(len(data.get('text', []))):
                        word = (data['text'][i] or '').strip()
                        try:
                            conf = float(data['conf'][i]) if data['conf'][i] not in (None, '', '-1') else -1.0
                        except Exception:
                            conf = -1.0
                        if word and conf >= 0:
                            tokens.append({
                                "word": word,
                                "conf": conf,
                                "bbox": [int(data['left'][i]), int(data['top'][i]), int(data['width'][i]), int(data['height'][i])],
                                "line_num": int(data.get('line_num', [1]*len(data['text']))[i]) if 'line_num' in data else 1,
                                "block_num": int(data.get('block_num', [1]*len(data['text']))[i]) if 'block_num' in data else 1,
                            })
                    if not tokens:
                        continue
                    # Reconstruct text by line order
                    tokens_sorted = sorted(tokens, key=lambda t: (t['line_num'], t['bbox'][0]))
                    text = ' '.join(t['word'] for t in tokens_sorted)
                    mean_conf = sum(t['conf'] for t in tokens_sorted) / max(1, len(tokens_sorted))
                    score = self._score_ocr_result(text, mean_conf)
                    if score > best['score']:
                        best = {"text": text, "tokens": tokens_sorted, "mean_conf": mean_conf, "score": score}
                except Exception:
                    continue
        
        return {k: best[k] for k in ("text", "tokens", "mean_conf")}

    def _score_ocr_result(self, text: str, mean_conf: float) -> float:
        """Score an OCR attempt: prefer longer sensible text with higher confidence."""
        if not text:
            return -1.0
        words = [w for w in text.split() if w]
        if not words:
            return -1.0
        alpha_ratio = sum(1 for w in words if any(ch.isalpha() for ch in w)) / len(words)
        length_bonus = min(len(text) / 100.0, 1.0)
        return 0.6 * (mean_conf / 100.0) + 0.3 * alpha_ratio + 0.1 * length_bonus

    def _map_characters_to_words(self, characters: List[Dict[str, Any]], tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assign each detected character contour to the most likely word token.
        Returns list of mappings with word_index and char_index within that word.
        """
        mapped = []
        if not characters or not tokens:
            return mapped
        
        # Precompute token centers and line ranges
        def center_of(bbox):
            x, y, w, h = bbox
            return (x + w/2.0, y + h/2.0)
        
        # Group tokens by line for better alignment
        from collections import defaultdict
        line_to_indices = defaultdict(list)
        for idx, t in enumerate(tokens):
            line_to_indices[t.get('line_num', 1)].append(idx)
        
        # Ensure tokens have indices on each line left-to-right
        for line, idxs in line_to_indices.items():
            idxs.sort(key=lambda i: tokens[i]['bbox'][0])
            for local_pos, i in enumerate(idxs):
                tokens[i]['_line_pos'] = local_pos
        
        # Map each character to nearest token on same line (by y overlap) or containing bbox
        for char in sorted(characters, key=lambda c: c.get('bbox', [0,0,0,0])[0]):
            cb = char.get('bbox', [0,0,0,0])
            cx, cy = center_of(cb)
            best_word = -1
            best_dist = float('inf')
            best_char_index = 0
            # Try direct containment first
            for wi, t in enumerate(tokens):
                x, y, w, h = t['bbox']
                if x <= cx <= x + w and y <= cy <= y + h:
                    best_word = wi
                    break
            if best_word == -1:
                # Choose token with minimal vertical distance, then horizontal distance
                for wi, t in enumerate(tokens):
                    x, y, w, h = t['bbox']
                    # Vertical distance: 0 if overlapping
                    if (y <= cy <= y + h) or (cy <= y + h and cy >= y):
                        vdist = 0
                    else:
                        vdist = min(abs(cy - y), abs(cy - (y + h)))
                    hdist = 0 if (x <= cx <= x + w) else min(abs(cx - x), abs(cx - (x + w)))
                    dist = vdist * 2 + hdist
                    if dist < best_dist:
                        best_dist = dist
                        best_word = wi
            if best_word == -1:
                continue
            
            # Estimate character index inside the word by relative x ordering among chars assigned to that word
            mapped.append({
                "word_index": best_word,
                "char_bbox": cb,
                "template_matches": char.get("template_matches", []),
                "errors": char.get("errors", []),
            })
        
        # Within each word, assign char_index left-to-right
        by_word = {}
        for i, m in enumerate(mapped):
            by_word.setdefault(m['word_index'], []).append((i, m))
        for wi, items in by_word.items():
            items.sort(key=lambda it: it[1]['char_bbox'][0])
            for local_idx, (orig_idx, m) in enumerate(items):
                mapped[orig_idx]['char_index'] = local_idx
        
        return mapped

    def _build_word_feedback(self, tokens: List[Dict[str, Any]], mapping: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate per-character errors into per-word actionable feedback."""
        if not tokens:
            return []
        from collections import defaultdict
        word_issues = defaultdict(list)
        for m in mapping:
            errs = m.get('errors', []) or []
            if not errs:
                continue
            # Choose primary error description
            primary = errs[0]
            letter_hint = None
            matches = m.get('template_matches', []) or []
            if matches and matches[0].get('confidence', 0) >= 0.5:
                letter_hint = matches[0].get('letter')
            word_issues[m['word_index']].append({
                "char_index": m.get('char_index', 0),
                "letter_hint": letter_hint,
                "description": primary.get('description', ''),
                "suggestion": primary.get('suggestion', '')
            })
        
        feedback = []
        for wi, token in enumerate(tokens):
            issues = sorted(word_issues.get(wi, []), key=lambda x: x['char_index'])
            if not issues:
                continue
            feedback.append({
                "word_index": wi,
                "word": token.get('word', ''),
                "issues": issues
            })
        return feedback
    
    def _preprocess_aggressive(self, image: Image.Image) -> Image.Image:
        """More aggressive preprocessing for difficult images"""
        from PIL import ImageEnhance, ImageFilter
        import numpy as np
        
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize larger
        width, height = image.size
        if width < 600 or height < 600:
            scale = max(600/width, 600/height)
            image = image.resize((int(width*scale), int(height*scale)))
        
        # Enhance more aggressively
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(3.0)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply different threshold
        img_array = np.array(image)
        threshold = np.percentile(img_array, 50)  # Use median as threshold
        img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(img_array)

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Basic image preprocessing"""
        from PIL import ImageEnhance
        import numpy as np
        
        if image.mode != 'L':
            image = image.convert('L')
        
        width, height = image.size
        if width < 300 or height < 300:
            scale = max(300/width, 300/height)
            image = image.resize((int(width*scale), int(height*scale)))
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        img_array = np.array(image)
        threshold = np.mean(img_array)
        img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(img_array)

    def _analyze_characters(self, image_path: str) -> Dict[str, Any]:
        """Enhanced character analysis with curve and stroke detection"""
        try:
            import cv2
            import numpy as np
            
            # Check if OpenCV can read the image
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                # Fallback: try with PIL and convert
                try:
                    pil_img = Image.open(image_path).convert('L')
                    img = np.array(pil_img)
                except:
                    return {"characters": [], "error": "Could not load image"}
            
            # Try different thresholding methods
            binary = None
            try:
                _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            except:
                # Fallback threshold
                threshold = np.mean(img)
                binary = np.where(img < threshold, 255, 0).astype(np.uint8)
            
            # Find contours with error handling
            try:
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            except:
                return {"characters": [], "error": "Could not find contours"}
            
            characters = []
            for i, contour in enumerate(contours):
                try:
                    area = cv2.contourArea(contour)
                    if area < 30:  # Lower threshold for small text
                        continue
                    
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Ensure valid bounding box
                    if w < 5 or h < 5:
                        continue
                    
                    char_img = binary[y:y+h, x:x+w]
                    
                    # Safe feature extraction
                    features = self._extract_geometric_features_safe(contour, char_img)
                    matches = self._enhanced_template_match_safe(char_img, features)
                    errors = self._analyze_character_errors_safe(char_img, features)
                    
                    characters.append({
                        "id": i,
                        "bbox": [x, y, w, h],
                        "features": features,
                        "template_matches": matches,
                        "errors": errors
                    })
                except Exception as char_error:
                    # Skip problematic characters but continue
                    continue
            
            # Generate visual overlay (optional, don't fail if it doesn't work)
            overlay_path = ""
            try:
                overlay_path = self._generate_visual_overlay(image_path, {"characters": characters})
            except:
                pass
            
            return {
                "characters": characters,
                "total_found": len(characters),
                "visual_overlay_path": overlay_path
            }
            
        except Exception as e:
            return {"characters": [], "error": f"Character analysis failed: {str(e)}"}
    
    def _extract_geometric_features_safe(self, contour, char_img) -> Dict[str, Any]:
        """Safe version of geometric feature extraction"""
        try:
            return self._extract_geometric_features(contour, char_img)
        except:
            # Return basic features if detailed analysis fails
            return {
                "area": 100,
                "aspect_ratio": 1.0,
                "has_loops": False,
                "has_curves": False,
                "stroke_count": 1
            }
    
    def _enhanced_template_match_safe(self, char_img, features) -> List[Dict[str, Any]]:
        """Safe version of template matching"""
        try:
            return self._enhanced_template_match(char_img, features)
        except:
            return [{"letter": "?", "confidence": 0.1, "reasoning": "Could not analyze"}]
    
    def _analyze_character_errors_safe(self, char_img, features) -> List[Dict[str, str]]:
        """Safe version of error analysis"""
        try:
            return self._analyze_character_errors(char_img, features)
        except:
            return []
    
    def _detect_loops(self, char_img) -> bool:
        """Simple loop detection"""
        try:
            import cv2
            contours, hierarchy = cv2.findContours(char_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            if hierarchy is not None:
                for i, h in enumerate(hierarchy[0]):
                    if h[3] != -1 and cv2.contourArea(contours[i]) > 20:
                        return True
        except:
            pass
        return False
    
    def _extract_geometric_features(self, contour, char_img) -> Dict[str, Any]:
        """Extract detailed geometric features for character analysis"""
        import cv2
        import numpy as np
        
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        features = {
            "area": area,
            "perimeter": perimeter,
            "aspect_ratio": char_img.shape[1] / char_img.shape[0] if char_img.shape[0] > 0 else 0,
            "circularity": 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0,
            "has_loops": self._detect_loops(char_img),
            "has_curves": self._detect_curves(contour),
            "stroke_count": self._count_strokes(char_img),
            "is_closed": self._is_shape_closed(contour)
        }
        
        # Convex hull analysis
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        features["solidity"] = area / hull_area if hull_area > 0 else 0
        
        return features
    
    def _detect_curves(self, contour) -> bool:
        """Detect significant curves in character contour"""
        import cv2
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        return len(approx) > 6  # More vertices suggest curves
    
    def _count_strokes(self, char_img) -> int:
        """Count number of separate strokes in character"""
        import cv2
        contours, _ = cv2.findContours(char_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len([c for c in contours if cv2.contourArea(c) > 10])
    
    def _is_shape_closed(self, contour) -> bool:
        """Check if character shape is closed"""
        import cv2
        return cv2.isContourConvex(contour) or len(contour) > 20
    
    def _enhanced_template_match(self, char_img, features) -> List[Dict[str, Any]]:
        """OCR-based character recognition instead of template matching"""
        try:
            import pytesseract
            from PIL import Image
            import numpy as np
            
            if char_img.shape[0] == 0 or char_img.shape[1] == 0:
                return []
            
            # Convert to PIL Image for Tesseract
            pil_img = Image.fromarray(char_img)
            
            # Use Tesseract to recognize single character
            config = '--psm 10 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            
            try:
                # Get character and confidence from Tesseract
                data = pytesseract.image_to_data(pil_img, config=config, output_type=pytesseract.Output.DICT)
                
                matches = []
                for i in range(len(data['text'])):
                    char = data['text'][i].strip()
                    conf = float(data['conf'][i]) if data['conf'][i] not in (None, '', '-1') else 0
                    
                    if char and conf > 10:  # Very low threshold
                        matches.append({
                            "letter": char.lower(),
                            "confidence": conf / 100.0,
                            "reasoning": f"OCR recognition of '{char}'"
                        })
                
                return sorted(matches, key=lambda x: x["confidence"], reverse=True)[:3]
                
            except:
                return []
                
        except ImportError:
            # Fallback to simple template matching if Tesseract not available
            return []
    
    def _get_match_reasoning(self, letter: str, features: Dict) -> str:
        """Generate detailed reasoning for template matches"""
        has_loop = features.get("has_loops", False)
        has_curves = features.get("has_curves", False)
        aspect_ratio = features.get("aspect_ratio", 1.0)
        circularity = features.get("circularity", 0)
        
        reasoning_map = {
            'O': f"Circular shape (circularity: {circularity:.2f})" + (" with loop" if has_loop else ""),
            'I': f"Vertical structure (aspect ratio: {aspect_ratio:.2f})" + (" with straight lines" if not has_curves else ""),
            'b': f"Upper loop detected" if has_loop else f"Vertical stem with curve (curves: {has_curves})",
            'd': f"Right-side loop" if has_loop else f"Curved right side (curves: {has_curves})",
            'p': f"Lower extension with loop" if has_loop else f"Descender with curve"
        }
        
        return reasoning_map.get(letter, f"Shape similarity to {letter}")
    
    def _analyze_character_errors(self, char_img, features: Dict) -> List[Dict[str, str]]:
        """Analyze per-character errors and provide specific feedback"""
        errors = []
        
        # Check for incomplete curves
        if features.get("has_curves") and features.get("circularity", 0) < 0.3:
            errors.append({
                "type": "incomplete_curve",
                "description": "Curve appears incomplete or irregular",
                "suggestion": "Practice smooth, continuous curves"
            })
        
        # Check for unclosed loops
        if not features.get("has_loops") and features.get("circularity", 0) > 0.6:
            errors.append({
                "type": "unclosed_loop",
                "description": "Loop may not be properly closed",
                "suggestion": "Ensure loops are completely closed"
            })
        
        # Check aspect ratio issues
        aspect_ratio = features.get("aspect_ratio", 1.0)
        if aspect_ratio > 2.5:
            errors.append({
                "type": "flipped_letter",
                "description": "Character appears unusually wide, possibly flipped",
                "suggestion": "Check letter orientation (b vs d, p vs q)"
            })
        elif aspect_ratio < 0.3:
            errors.append({
                "type": "compressed_letter",
                "description": "Character appears too tall or compressed",
                "suggestion": "Maintain consistent letter proportions"
            })
        
        # Check for broken strokes
        if features.get("stroke_count", 1) > 2:
            errors.append({
                "type": "broken_stroke",
                "description": "Character has disconnected parts",
                "suggestion": "Write with continuous, connected strokes"
            })
        
        return errors
    
    def _generate_visual_overlay(self, image_path: str, character_analysis: Dict) -> str:
        """Generate visual overlay with character highlights and annotations"""
        try:
            import cv2
            import numpy as np
            
            img = cv2.imread(image_path)
            if img is None:
                return ""
            
            overlay = img.copy()
            
            for char in character_analysis.get("characters", []):
                x, y, w, h = char["bbox"]
                
                # Color coding based on analysis
                matches = char.get("template_matches", [])
                errors = char.get("errors", [])
                
                if errors:
                    color = (0, 0, 255)  # Red for errors
                elif matches and matches[0]["confidence"] > 0.7:
                    color = (0, 255, 0)  # Green for high confidence
                elif matches and matches[0]["confidence"] > 0.4:
                    color = (0, 255, 255)  # Yellow for medium confidence
                else:
                    color = (255, 0, 0)  # Blue for low confidence
                
                # Draw bounding box
                cv2.rectangle(overlay, (x, y), (x+w, y+h), color, 2)
                
                # Add character label
                if matches:
                    label = f"{matches[0]['letter']} ({matches[0]['confidence']:.2f})"
                    cv2.putText(overlay, label, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
                # Mark error zones
                if errors:
                    cv2.circle(overlay, (x+w//2, y+h//2), 3, (255, 0, 255), -1)
            
            # Save overlay
            overlay_path = image_path.replace('.', '_overlay.')
            cv2.imwrite(overlay_path, overlay)
            return overlay_path
            
        except Exception as e:
            return f"Error: {str(e)}"

    def _generate_visual_overlay_with_words(self, image_path: str, character_analysis: Dict, tokens: List[Dict[str, Any]], word_feedback: List[Dict[str, Any]]) -> str:
        """Generate overlay that includes word boxes and indices in addition to character annotations."""
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return ""
            overlay = img.copy()
            
            # Draw word boxes
            for i, t in enumerate(tokens):
                x, y, w, h = t.get('bbox', [0,0,0,0])
                cv2.rectangle(overlay, (x, y), (x+w, y+h), (255, 255, 0), 2)  # Cyan
                cv2.putText(overlay, f"W{i}", (x, y-4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Draw characters as in basic overlay
            for char in character_analysis.get("characters", []):
                x, y, w, h = char["bbox"]
                matches = char.get("template_matches", [])
                errors = char.get("errors", [])
                if errors:
                    color = (0, 0, 255)
                elif matches and matches[0].get("confidence", 0) > 0.7:
                    color = (0, 255, 0)
                elif matches and matches[0].get("confidence", 0) > 0.4:
                    color = (0, 255, 255)
                else:
                    color = (255, 0, 0)
                cv2.rectangle(overlay, (x, y), (x+w, y+h), color, 1)
                if errors:
                    cv2.circle(overlay, (x+w//2, y+h//2), 3, (255, 0, 255), -1)
            
            # Annotate issues near words
            for wf in (word_feedback or []):
                wi = wf.get('word_index')
                if wi is None or wi < 0 or wi >= len(tokens):
                    continue
                x, y, w, h = tokens[wi].get('bbox', [0,0,0,0])
                label = f"{wf.get('word','')}"
                cv2.putText(overlay, label, (x, y+h+14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
                # Show first issue succinctly
                if wf.get('issues'):
                    issue = wf['issues'][0]
                    hint = issue.get('letter_hint') or '?'
                    desc = issue.get('description','')
                    cv2.putText(overlay, f"c{issue.get('char_index',0)}:{hint}", (x, y+h+28), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)
            
            overlay_path = image_path.replace('.', '_overlay_words.')
            cv2.imwrite(overlay_path, overlay)
            return overlay_path
        except Exception as e:
            return ""
    
    def _create_a_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.ellipse(template, (16, 20), (8, 8), 0, 0, 360, 255, 2)
        cv2.line(template, (24, 12), (24, 28), 255, 2)
        return template
    
    def _create_c_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.ellipse(template, (16, 16), (8, 8), 0, 45, 315, 255, 2)
        return template
    
    def _create_e_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.ellipse(template, (16, 16), (8, 8), 0, 0, 360, 255, 2)
        cv2.line(template, (16, 16), (24, 16), 255, 2)
        return template
    
    def _create_g_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.ellipse(template, (16, 16), (8, 8), 0, 0, 360, 255, 2)
        cv2.line(template, (24, 16), (24, 30), 255, 2)
        return template
    
    def _create_h_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 4), (8, 28), 255, 2)
        cv2.line(template, (24, 12), (24, 28), 255, 2)
        cv2.line(template, (8, 16), (24, 16), 255, 2)
        return template
    
    def _create_i_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (16, 12), (16, 28), 255, 2)
        cv2.circle(template, (16, 8), 2, 255, -1)
        return template
    
    def _create_l_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (16, 4), (16, 28), 255, 2)
        return template
    
    def _create_m_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 12), (8, 28), 255, 2)
        cv2.line(template, (16, 12), (16, 28), 255, 2)
        cv2.line(template, (24, 12), (24, 28), 255, 2)
        cv2.ellipse(template, (12, 16), (4, 4), 0, 0, 180, 255, 2)
        cv2.ellipse(template, (20, 16), (4, 4), 0, 0, 180, 255, 2)
        return template
    
    def _create_n_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 12), (8, 28), 255, 2)
        cv2.line(template, (24, 12), (24, 28), 255, 2)
        cv2.ellipse(template, (16, 16), (8, 4), 0, 0, 180, 255, 2)
        return template
    
    def _create_o_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.ellipse(template, (16, 16), (8, 8), 0, 0, 360, 255, 2)
        return template
    
    def _create_r_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 12), (8, 28), 255, 2)
        cv2.ellipse(template, (16, 16), (8, 4), 0, 270, 90, 255, 2)
        return template
    
    def _create_s_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.ellipse(template, (16, 14), (6, 4), 0, 180, 360, 255, 2)
        cv2.ellipse(template, (16, 22), (6, 4), 0, 0, 180, 255, 2)
        return template
    
    def _create_t_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (16, 8), (16, 28), 255, 2)
        cv2.line(template, (8, 12), (24, 12), 255, 2)
        return template
    
    def _create_u_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 12), (8, 24), 255, 2)
        cv2.line(template, (24, 12), (24, 28), 255, 2)
        cv2.ellipse(template, (16, 24), (8, 4), 0, 0, 180, 255, 2)
        return template
    
    def _create_w_template(self):
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (6, 12), (10, 28), 255, 2)
        cv2.line(template, (10, 28), (16, 20), 255, 2)
        cv2.line(template, (16, 20), (22, 28), 255, 2)
        cv2.line(template, (22, 28), (26, 12), 255, 2)
        return template
    
    def _create_b_template(self):
        """Create 'b' template with upper loop"""
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 4), (8, 28), 255, 2)  # Vertical line
        cv2.ellipse(template, (16, 12), (8, 6), 0, 0, 180, 255, 2)  # Upper curve
        return template
    
    def _create_d_template(self):
        """Create 'd' template with right loop"""
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (24, 4), (24, 28), 255, 2)  # Vertical line
        cv2.ellipse(template, (16, 16), (8, 8), 0, 90, 270, 255, 2)  # Left curve
        return template
    
    def _create_p_template(self):
        """Create 'p' template with descender"""
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (8, 12), (8, 30), 255, 2)  # Vertical line with descender
        cv2.ellipse(template, (16, 16), (8, 4), 0, 270, 90, 255, 2)  # Upper curve
        return template

    def _analyze_image_quality(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image quality"""
        import numpy as np
        
        img_array = np.array(image.convert('L'))
        
        analysis = {
            "brightness": np.mean(img_array),
            "contrast": np.std(img_array),
            "sharpness": self._calculate_sharpness(img_array),
            "text_density": self._estimate_text_density(img_array),
            "image_size": image.size,
            "issues": [],
            "suggestions": []
        }
        
        if analysis["brightness"] < 80:
            analysis["issues"].append("Image is too dark")
            analysis["suggestions"].append("Increase lighting")
        elif analysis["brightness"] > 200:
            analysis["issues"].append("Image is overexposed")
            analysis["suggestions"].append("Reduce lighting")
        
        if analysis["contrast"] < 30:
            analysis["issues"].append("Low contrast")
            analysis["suggestions"].append("Use darker ink")
        
        if analysis["sharpness"] < 50:
            analysis["issues"].append("Image appears blurry")
            analysis["suggestions"].append("Hold camera steady")
        
        width, height = analysis["image_size"]
        if width < 300 or height < 300:
            analysis["issues"].append("Low resolution")
            analysis["suggestions"].append("Take photo closer")
        
        if analysis["text_density"] < 0.02:
            analysis["issues"].append("Very little text detected")
            analysis["suggestions"].append("Ensure handwriting fills image")
        
        return analysis
    
    def _calculate_sharpness(self, img_array) -> float:
        """Simple sharpness calculation"""
        import numpy as np
        edges = np.abs(np.diff(img_array, axis=0)).sum() + np.abs(np.diff(img_array, axis=1)).sum()
        return edges / img_array.size
    
    def _estimate_text_density(self, img_array) -> float:
        """Estimate text density"""
        import numpy as np
        threshold = np.mean(img_array) - np.std(img_array)
        text_pixels = np.sum(img_array < threshold)
        return text_pixels / img_array.size
    
    def _post_process_text(self, text: str) -> str:
        """Post-process OCR text"""
        if not text:
            return text
            
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        corrections = {'rn': 'm', 'cl': 'd', 'vv': 'w', 'ii': 'n'}
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        text = re.sub(r'\b1\b', 'I', text)
        text = re.sub(r'\b0\b', 'O', text)
        text = re.sub(r'(.)\1{3,}', r'\1', text)
        
        return text
    
    def _analyze_basic_errors(self, text: str) -> List[Dict[str, Any]]:
        """Basic error detection"""
        errors = []
        
        common_ocr_errors = {
            '0': 'O', '1': 'I', '5': 'S', '8': 'B',
            'cl': 'd', 'rn': 'm', 'vv': 'w', 'ii': 'n'
        }
        
        for wrong, correct in common_ocr_errors.items():
            if wrong in text:
                errors.append({
                    "type": "ocr_confusion",
                    "detected": wrong,
                    "suggestion": correct,
                    "description": f"'{wrong}' might be '{correct}'"
                })
        
        return errors
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate confidence"""
        if not text.strip():
            return 0.0
        
        confidence = 0.4
        readable_chars = sum(1 for c in text if c.isalnum() or c.isspace())
        total_chars = len(text)
        
        if total_chars > 0:
            readable_ratio = readable_chars / total_chars
            confidence += readable_ratio * 0.4
        
        words = text.split()
        if words:
            valid_words = sum(1 for word in words if len(word) >= 2 and word.isalpha())
            word_ratio = valid_words / len(words)
            confidence += word_ratio * 0.2
        
        if len(text.strip()) < 3:
            confidence *= 0.7
        
        return min(1.0, confidence)

class HandwritingAnalyzer:
    """Minimal handwriting analysis"""
    
    def __init__(self):
        self.processor = TesseractOCRProcessor()
    
    async def recognize_handwriting(self, image_path: str, language: str = "en") -> Dict[str, Any]:
        return await self.processor.recognize_handwriting(image_path, language)
    
    async def correct_handwriting(self, image_path: str, language: str = "en") -> Dict[str, Any]:
        result = await self.recognize_handwriting(image_path, language)
        
        if not result.get("success"):
            return result
        
        text = result["recognized_text"]
        corrected = text.replace('teh', 'the').replace('adn', 'and')
        
        return {
            **result,
            "corrected_text": corrected,
            "corrections_applied": ["Basic corrections applied"] if corrected != text else []
        }

handwriting_recognizer = HandwritingAnalyzer()