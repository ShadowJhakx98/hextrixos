#!/bin/bash

# Configuration
PORT=${1:-3000}  # Use the first argument as port, or default to 3000
MCP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Print banner
echo "╔════════════════════════════════════════════╗"
echo "║        Hextrix OS MCP Server Starter       ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Starting MCP server on port $PORT..."
echo "Press Ctrl+C to stop the server"
echo ""

# Export the port
export PORT

# Change to the MCP directory
cd "$MCP_DIR"

# Start the server
node index.js 