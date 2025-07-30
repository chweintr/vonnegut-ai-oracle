#!/bin/bash

# Setup script for experimental development
# This keeps production safe while allowing experimentation

echo "🔬 Setting up experimental environment for Vonnegut AI..."

# Create experimental branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/experimental; then
    echo "Creating experimental branch..."
    git checkout -b experimental
else
    echo "Switching to experimental branch..."
    git checkout experimental
fi

# Copy stable version to experimental file
cp app.py experimental_app.py
echo "✅ Created experimental_app.py from stable version"

# Create experimental railway.json
cat > railway_experimental.json << 'EOF'
{
  "build": {
    "commands": [
      "pip install -r requirements.txt"
    ]
  },
  "deploy": {
    "startCommand": "streamlit run experimental_app.py --server.port $PORT --server.address 0.0.0.0"
  }
}
EOF

echo "✅ Created railway_experimental.json"

# Create a test script
cat > test_local.sh << 'EOF'
#!/bin/bash
echo "🧪 Starting local test server..."
echo "📝 Remember to test:"
echo "  1. Text → Text mode"
echo "  2. Text → Audio mode"
echo "  3. Audio → Audio mode"
echo ""
streamlit run experimental_app.py
EOF

chmod +x test_local.sh

echo ""
echo "🎉 Experimental environment ready!"
echo ""
echo "📋 Next steps:"
echo "1. Make your changes to experimental_app.py"
echo "2. Test locally with: ./test_local.sh"
echo "3. If you want to deploy to a separate Railway app:"
echo "   - Create new app: railway create vonnegut-experimental"
echo "   - Link this branch: railway link vonnegut-experimental"
echo "   - Deploy: railway up"
echo ""
echo "⚠️  NEVER merge experimental to main without thorough testing!"
echo ""