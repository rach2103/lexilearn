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
        """Recognize handwriting with character analysis"""
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
            
            # Try multiple OCR approaches
            text = self._try_multiple_ocr_configs(image, language)
            
            # Always run character analysis even if OCR fails
            character_analysis = self._analyze_characters(image_path)
            
            # Post-process text if we got any
            if text:
                text = self._post_process_text(text)
            
            return {
                "success": True,
                "recognized_text": text,
                "confidence": self._estimate_confidence(text),
                "errors": self._analyze_basic_errors(text),
                "image_analysis": self._analyze_image_quality(image),
                "character_analysis": character_analysis,
                "visual_overlay_path": character_analysis.get("visual_overlay_path", "")
            }
            
        except Exception as e:
            return {
                "success": False, 
                "error": str(e), 
                "character_analysis": {"characters": []},
                "recognized_text": "",
                "confidence": 0.0
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
        """Enhanced template matching with feature-based reasoning"""
        try:
            import cv2
            import numpy as np
            
            if char_img.shape[0] == 0 or char_img.shape[1] == 0:
                return []
            
            char_resized = cv2.resize(char_img, (32, 32))
            
            # Extended template set
            templates = {
                'O': self._create_circle_template(),
                'I': self._create_line_template(),
                'b': self._create_b_template(),
                'd': self._create_d_template(),
                'p': self._create_p_template()
            }
            
            matches = []
            for letter, template in templates.items():
                result = cv2.matchTemplate(char_resized, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                
                if max_val > 0.25:
                    reasoning = self._get_match_reasoning(letter, features)
                    matches.append({
                        "letter": letter,
                        "confidence": float(max_val),
                        "reasoning": reasoning
                    })
            
            return sorted(matches, key=lambda x: x["confidence"], reverse=True)[:3]
        except:
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
    
    def _create_circle_template(self):
        """Create circle template"""
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.circle(template, (16, 16), 12, 255, 2)
        return template
    
    def _create_line_template(self):
        """Create line template"""
        import cv2
        import numpy as np
        template = np.zeros((32, 32), dtype=np.uint8)
        cv2.line(template, (16, 4), (16, 28), 255, 2)
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