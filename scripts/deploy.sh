#!/bin/bash
set -e

echo "🚀 Starting Deployment..."

# 1. Backend Setup
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
playwright install chromium

# 2. Frontend Build
echo "🎨 Building Frontend..."
cd web
npm install
npm run build
cd ..

# 3. Blog Build
echo "📝 Building Blog..."
cd blog
bundle install
bundle exec jekyll build
cd ..

echo "✅ Build Complete!"
echo "-----------------------------------"
echo "To start the services:"
echo "1. API & Webhook: python api/multilingual_api.py & python api/webhook_server.py"
echo "2. Frontend: serve -s web/dist -l 5173"
echo "3. Blog: serve -s blog/_site -l 4000"
echo "-----------------------------------"
