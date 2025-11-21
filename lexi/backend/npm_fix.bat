@echo off
echo Fixing npm node.exe issue...
npm config set scripts-prepend-node-path true
npm config set node-gyp "C:\Program Files\nodejs\node_modules\npm\node_modules\node-gyp\bin\node-gyp.js"
refreshenv
echo Fixed. Try npm install again.
pause