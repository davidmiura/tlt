# === Config ===
PYTHON=python
PYTHONPATH=.
INSPECTOR_PORT_BASE=880
SERVER_PORT_BASE=800

# === MCP service entrypoints ===
EVAL_ENTRY=tlt/mcp_services/eval/server.py
EVENT_MANAGER_ENTRY=tlt/mcp_services/event_manager/main.py
GATEWAY_ENTRY=tlt/mcp_services/gateway/main.py
GUILD_MANAGER_ENTRY=tlt/mcp_services/guild_manager/main.py
PHOTO_VIBE_CHECK_ENTRY=tlt/mcp_services/photo_vibe_check/main.py
RSVP_ENTRY=tlt/mcp_services/rsvp/main.py
VIBE_BIT_ENTRY=tlt/mcp_services/vibe_bit/main.py

# === Wrapper Script Generation ===

wrap-eval:
	@echo "🔧 Generating mcp-server-gateway wrapper"
	echo '#!/bin/bash\nPYTHONPATH=. poetry run $(PYTHON) $(GATEWAY_ENTRY)' > mcp-server-gateway
	chmod +x mcp-server-gateway

wrap-gateway:
	@echo "🔧 Generating mcp-server-gateway wrapper"
	echo '#!/bin/bash\nPYTHONPATH=. poetry run $(PYTHON) $(GATEWAY_ENTRY)' > mcp-server-gateway
	chmod +x mcp-server-gateway

wrap-chat:
	@echo "🔧 Generating mcp-server-chat wrapper"
	echo '#!/bin/bash\nPYTHONPATH=. poetry run $(PYTHON) $(CHAT_ENTRY)' > mcp-server-chat
	chmod +x mcp-server-chat

wrap-user:
	@echo "🔧 Generating mcp-server-user wrapper"
	echo '#!/bin/bash\nPYTHONPATH=. poetry run $(PYTHON) $(USER_ENTRY)' > mcp-server-user
	chmod +x mcp-server-user

wrap-all: wrap-gateway wrap-chat wrap-user

# === MCP Servce Production Mode ===

run-gateway:
	@echo "🚀 Running gateway MCP service"
	PATH=".:$$PATH" PYTHONPATH=$(PYTHONPATH) fastmcp dev $(GATEWAY_ENTRY) --server_port=$(SERVER_PORT_BASE)3 --ui_port=$(INSPECTOR_PORT_BASE)3



# === MCP Service Dev Mode ===



PYTHONPATH=. ENV=production fastmcp run tlt/mcp_services/gateway/main.py --transport streamable-http --port 8003


dev-gateway:
	@echo "🚀 Running gateway MCP service"
	PATH=".:$$PATH" PYTHONPATH=$(PYTHONPATH) fastmcp dev $(GATEWAY_ENTRY) --server_port=$(SERVER_PORT_BASE)3 --ui_port=$(INSPECTOR_PORT_BASE)3

dev-chat:
	@echo "🚀 Running Chat MCP service"
	PATH=".:$$PATH" PYTHONPATH=$(PYTHONPATH) fastmcp dev $(CHAT_ENTRY) --server_port=$(SERVER_PORT_BASE)2 --ui_port=$(INSPECTOR_PORT_BASE)2

dev-user:
	@echo "🚀 Running User MCP service"
	PATH=".:$$PATH" PYTHONPATH=$(PYTHONPATH) fastmcp dev $(USER_ENTRY) --server_port=$(SERVER_PORT_BASE)5 --ui_port=$(INSPECTOR_PORT_BASE)5

# === Open Inspector URLs ===

open-gateway:
	open "http://localhost:8803/?MCP_PROXY_PORT=8001&command=mcp-server-gateway"

open-chat:
	open "http://localhost:8802/?MCP_PROXY_PORT=8002&command=mcp-server-chat"

open-user:
	open "http://localhost:8805/?MCP_PROXY_PORT=8003&command=mcp-server-user"

# === Help ===

.PHONY: help
help:
	@echo "🛠  MCP Service Commands:"
	@echo "  make wrap-gateway     - Generate wrapper for gateway MCP"
	@echo "  make wrap-chat      - Generate wrapper for Chat MCP"
	@echo "  make wrap-user      - Generate wrapper for User MCP"
	@echo "  make wrap-all       - Generate all wrappers"
	@echo "  make run-gateway      - Start gateway MCP with FastMCP"
	@echo "  make open-gateway     - Open Inspector for gateway MCP"
