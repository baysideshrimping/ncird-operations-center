@echo off
echo ================================================
echo Pushing NCIRD Operations Center to GitHub
echo ================================================
echo.
echo Make sure you created the repo at:
echo https://github.com/new
echo.
echo Repo name: ncird-operations-center
echo.
pause

cd /d C:\Users\kevin\ncird-operations-center

echo Adding remote...
git remote add origin https://github.com/baysideshrimping/ncird-operations-center.git

echo Renaming branch to main...
git branch -M main

echo Pushing to GitHub...
git push -u origin main

echo.
echo ================================================
echo SUCCESS! Repository pushed to GitHub
echo ================================================
echo.
echo View at: https://github.com/baysideshrimping/ncird-operations-center
echo.
echo Next: Deploy to Render
echo Go to: https://dashboard.render.com/
echo.
pause
