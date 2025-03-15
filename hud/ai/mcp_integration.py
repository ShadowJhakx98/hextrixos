#!/usr/bin/env python3
# MCP Integration Module for Hextrix AI
# This module allows the AI to control system components through MCP

import os
import sys
import json
import subprocess
import re
import requests
import logging
import time

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mcp_integration.log')

# Set up logging with both console and file handlers
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_integration")

# Add file handler
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Log startup message
logger.info("MCP Integration module initialized, logging to %s", log_file)

# Import MCP client
sys.path.append('/home/jared/hextrix-ai-os-env')
try:
    from hextrix_mcp.mcp_client import HextrixMCPClient
except ImportError:
    logger.warning("Could not import HextrixMCPClient from MCP. Some features may be limited.")
    HextrixMCPClient = None
    
class MCPIntegration:
    """Integration with MCP to control system apps, files, and services"""
    
    def __init__(self):
        """Initialize MCP integration"""
        # Try to initialize the MCP client if available
        self.mcp = None
        if HextrixMCPClient:
            try:
                self.mcp = HextrixMCPClient(base_url="http://localhost:3000")
            except Exception as e:
                logger.warning(f"Failed to initialize HextrixMCPClient: {e}")
        
        # Load API keys for external services
        self.api_keys = {}
        self.load_api_keys()
        
        # Initialize capabilities cache
        self.capabilities = None
        self.refresh_capabilities()
        
    def load_api_keys(self):
        """Load API keys from credentials file"""
        try:
            credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../credentials2.json')
            if os.path.exists(credentials_path):
                with open(credentials_path, 'r') as f:
                    credentials = json.load(f)
                    # Store all keys in the api_keys dictionary
                    self.api_keys = credentials.get('api_keys', {})
                    logger.info("API keys loaded successfully")
            else:
                logger.warning(f"Credentials file not found at {credentials_path}")
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
        
    def refresh_capabilities(self):
        """Refresh MCP capabilities"""
        # Initialize with basic capabilities
        self.capabilities = {
            "fileSystem": True,  # Basic file system operations always available
            "systemInfo": True,  # System information always available
        }
        
        # Add existing MCP capabilities if available
        if self.mcp:
            try:
                mcp_capabilities = self.mcp.get_capabilities()
                if mcp_capabilities:
                    self.capabilities.update(mcp_capabilities)
            except Exception as e:
                logger.error(f"Error getting MCP capabilities: {e}")
        
        # Check for external service capabilities based on API keys
        # For Trieve RAG
        if self.api_keys.get('trieve_api_key'):
            self.capabilities['trieveRAG'] = True
        
        # For Perplexity Research - use existing "perplexity" key if available
        if self.api_keys.get('perplexity_api_key') or self.api_keys.get('perplexity'):
            self.capabilities['perplexityResearch'] = True
        
        # For Google Search via SerpAPI - use existing "serp" key if available
        if self.api_keys.get('serpapi_api_key') or self.api_keys.get('serp'):
            self.capabilities['googleSearch'] = True
        
        # For News Search via NewsAPI
        if self.api_keys.get('newsapi_api_key'):
            self.capabilities['newsSearch'] = True
            
        return True
    
    #-------------------------------------------------------------------
    # File System Operations
    #-------------------------------------------------------------------
    
    def search_files(self, query, directory=None, recursive=True):
        """Search for files matching a query"""
        # First try the specialized search methods based on query prefixes
        if query.startswith("news:") and self.capabilities.get('newsSearch'):
            return self.search_news(query[5:].strip())
        elif query.startswith("web:") and self.capabilities.get('googleSearch'):
            return self.search_web(query[4:].strip())
        elif query.startswith("research:") and self.capabilities.get('perplexityResearch'):
            return self.research_topic(query[9:].strip())
        elif query.startswith("rag:") and self.capabilities.get('trieveRAG'):
            return self.search_with_rag(query[4:].strip())
        
        # If no specialized prefix, use MCP client or fall back to local implementation
        try:
            logger.info(f"Searching for files with query: '{query}'")
            
            if self.mcp:
                logger.info("Using HextrixMCPClient for file search")
                # Use MCP client if available
                if directory is None:
                    directory = os.path.expanduser("~")
                    logger.info(f"Using default directory: {directory}")
                
                # Always try grep_files first for better search results
                if hasattr(self.mcp, 'grep_files'):
                    logger.info(f"Performing content search with mcp.grep_files({directory}, {query}, {recursive})")
                    try:
                        result = self.mcp.grep_files(directory, query, recursive)
                        logger.info(f"MCP grep returned {len(result) if isinstance(result, list) else 'non-list'} results")
                        
                        # Format grep results to match file search results
                        formatted_results = []
                        for item in result:
                            if isinstance(item, dict):
                                file_path = item.get('file', '')
                                line_content = item.get('line', '')
                                line_number = item.get('lineNumber', '')
                                
                                formatted_results.append({
                                    'path': file_path,
                                    'content': f"Line {line_number}: {line_content}"
                                })
                            else:
                                formatted_results.append(item)
                        
                        # If we found results, return them
                        if formatted_results:
                            return formatted_results
                    except Exception as e:
                        logger.warning(f"Error using grep_files: {e}")
                
                # Fall back to search_files if grep_files failed or returned no results
                if hasattr(self.mcp, 'search_files'):
                    logger.info(f"Falling back to filename search with mcp.search_files({directory}, {query}, {recursive})")
                    try:
                        result = self.mcp.search_files(directory, query, recursive)
                        logger.info(f"MCP search returned {len(result) if isinstance(result, list) else 'non-list'} results")
                        return result
                    except Exception as e:
                        logger.warning(f"Error using search_files: {e}")
                
                # If we get here, neither search_files nor grep_files worked
                logger.warning("HextrixMCPClient methods failed, falling back to local search")
                return self.search_local_files(query)
            else:
                # Fall back to local file search
                logger.info("MCP client not available, using local file search")
                return self.search_local_files(query)
        except Exception as e:
            logger.error(f"Error in search_files: {e}", exc_info=True)
            return {"error": str(e)}
    
    def search_local_files(self, query):
        """Search local files in the system"""
        try:
            import subprocess
            import os
            
            start_time = time.time()
            logger.info(f"Starting file search for query: '{query}'")
            
            # Clean the query for use in shell commands
            clean_query = query.replace("'", "").replace('"', "").replace(";", "").replace("&", "")
            logger.info(f"Cleaned query: '{clean_query}'")
            
            # Check if this looks like an exact filename search
            is_exact_filename = False
            if "." in clean_query and " " not in clean_query:
                is_exact_filename = True
                logger.info(f"Query appears to be an exact filename")
            
            files = []
            
            # First try exact match if it looks like a filename
            if is_exact_filename:
                logger.info(f"Performing exact filename search for: {clean_query}")
                
                # Try plocate first as it's usually faster
                try:
                    logger.info("Trying plocate for exact filename")
                    locate_result = subprocess.run(
                        f"plocate -l 20 '{clean_query}'",
                        shell=True, capture_output=True, text=True
                    )
                    
                    # If plocate found results, use them
                    if locate_result.stdout.strip():
                        for file_path in locate_result.stdout.strip().split('\n'):
                            if file_path and os.path.isfile(file_path):
                                files.append({
                                    'path': file_path,
                                    'content': f"File found: {file_path}"
                                })
                        
                        # If we found exact matches, return them immediately
                        if files:
                            logger.info(f"Found {len(files)} exact matches using plocate in {time.time() - start_time:.2f} seconds")
                            return files
                except Exception as e:
                    logger.warning(f"plocate command failed: {e}")
                
                # Fall back to find if plocate didn't work or find no results
                logger.info("Falling back to find command for exact matches")
                
                # Try exact match first (case sensitive)
                logger.info("Trying case-sensitive exact match")
                exact_result = subprocess.run(
                    f"find /home/jared -type f -name '{clean_query}' -print 2>/dev/null | head -n 20",
                    shell=True, capture_output=True, text=True
                )
                
                # Then try case-insensitive match
                if not exact_result.stdout.strip():
                    logger.info("No case-sensitive matches, trying case-insensitive match")
                    exact_result = subprocess.run(
                        f"find /home/jared -type f -iname '{clean_query}' -print 2>/dev/null | head -n 20",
                        shell=True, capture_output=True, text=True
                    )
                
                # Add exact matches to results
                for file_path in exact_result.stdout.strip().split('\n'):
                    if file_path and os.path.exists(file_path):
                        files.append({
                            'path': file_path,
                            'content': f"File found: {file_path}"
                        })
                
                # If we found exact matches, return them immediately
                if files:
                    logger.info(f"Found {len(files)} exact matches for {clean_query} in {time.time() - start_time:.2f} seconds")
                    return files
            
            # If no exact matches or not an exact filename search, try partial match
            logger.info(f"Performing partial filename search for: {clean_query}")
            
            # Try plocate first as it's usually faster
            try:
                logger.info("Trying plocate for partial matches")
                locate_result = subprocess.run(
                    f"plocate -l 20 '*{clean_query}*'",
                    shell=True, capture_output=True, text=True
                )
                
                # Filter locate results to only include files (not directories)
                if locate_result.stdout.strip():
                    filtered_files = []
                    for file_path in locate_result.stdout.strip().split('\n'):
                        if file_path and os.path.isfile(file_path):
                            filtered_files.append(file_path)
                    
                    if filtered_files:
                        for file_path in filtered_files[:20]:  # Limit to 20 results
                            files.append({
                                'path': file_path,
                                'content': f"File found: {file_path}"
                            })
                        
                        logger.info(f"Found {len(files)} partial matches using plocate in {time.time() - start_time:.2f} seconds")
                        return files
            except Exception as e:
                logger.warning(f"plocate command failed: {e}")
            
            # Fall back to find command if plocate didn't work or find no results
            logger.info("Falling back to find command for partial matches")
            
            # Use find with wildcard pattern for partial matches
            # First try a more targeted search in common directories
            common_dirs = [
                "/home/jared/Documents", 
                "/home/jared/Downloads", 
                "/home/jared/Desktop",
                "/home/jared/hextrix-ai-os-env"
            ]
            
            for directory in common_dirs:
                if os.path.exists(directory):
                    logger.info(f"Searching in common directory: {directory}")
                    result = subprocess.run(
                        f"find {directory} -type f -iname '*{clean_query}*' -print 2>/dev/null | head -n 5",
                        shell=True, capture_output=True, text=True
                    )
                    
                    for file_path in result.stdout.strip().split('\n'):
                        if file_path and os.path.exists(file_path):
                            files.append({
                                'path': file_path,
                                'content': f"File found: {file_path}"
                            })
                    
                    # If we found enough files in common directories, return them
                    if len(files) >= 10:
                        logger.info(f"Found {len(files)} matches in common directories in {time.time() - start_time:.2f} seconds")
                        return files
            
            # If we still need more results, do a broader search
            if len(files) < 10:
                logger.info("Performing broader search in home directory")
                result = subprocess.run(
                    f"find /home/jared -type f -iname '*{clean_query}*' -print 2>/dev/null | head -n {20 - len(files)}",
                    shell=True, capture_output=True, text=True
                )
                
                for file_path in result.stdout.strip().split('\n'):
                    if file_path and os.path.exists(file_path) and not any(f.get('path') == file_path for f in files):
                        files.append({
                            'path': file_path,
                            'content': f"File found: {file_path}"
                        })
            
            logger.info(f"Found total of {len(files)} partial matches for {clean_query} in {time.time() - start_time:.2f} seconds")
            return files
        except Exception as e:
            logger.error(f"Error searching local files: {e}")
            return {"error": f"Error searching local files: {str(e)}"}
    
    def grep_text(self, query, directory=None, recursive=True):
        """Search for text content in files"""
        try:
            if self.mcp:
                if directory is None:
                    directory = os.path.expanduser("~")
                    
                return self.mcp.grep_text(directory, query, recursive)
            else:
                # Fall back to local grep implementation
                import subprocess
                
                if directory is None:
                    directory = os.path.expanduser("~")
                
                recursive_flag = "-r" if recursive else ""
                result = subprocess.run(
                    f"grep {recursive_flag} -l '{query}' {directory} 2>/dev/null | head -n 20",
                    shell=True, capture_output=True, text=True
                )
                
                files = []
                for file_path in result.stdout.strip().split('\n'):
                    if file_path:
                        files.append({
                            'path': file_path,
                            'content': f"Text found in: {file_path}"
                        })
                
                return files
        except Exception as e:
            return {"error": str(e)}
    
    def find_media(self, query, media_type="all"):
        """Find media files (images, videos, documents) matching a query"""
        try:
            if self.mcp:
                # Determine search directory based on media type
                if media_type == "images":
                    search_dir = os.path.expanduser("~/Pictures")
                elif media_type == "videos":
                    search_dir = os.path.expanduser("~/Videos")
                elif media_type == "documents":
                    search_dir = os.path.expanduser("~/Documents")
                else:
                    search_dir = os.path.expanduser("~")
                
                # Define extensions based on media type
                if media_type == "images":
                    extensions = "jpg,jpeg,png,gif,bmp,svg,webp"
                elif media_type == "videos":
                    extensions = "mp4,mkv,avi,mov,webm,flv"
                elif media_type == "documents":
                    extensions = "pdf,doc,docx,txt,rtf,odt,ppt,pptx,xls,xlsx"
                else:
                    extensions = None
                    
                # Execute the search
                return self.mcp.find_files(search_dir, query, extensions=extensions)
            else:
                # Fall back to local search
                import subprocess
                
                # Determine search directory and file extensions
                if media_type == "images":
                    search_dir = os.path.expanduser("~/Pictures")
                    ext_pattern = "-name '*.jpg' -o -name '*.jpeg' -o -name '*.png' -o -name '*.gif'"
                elif media_type == "videos":
                    search_dir = os.path.expanduser("~/Videos")
                    ext_pattern = "-name '*.mp4' -o -name '*.mkv' -o -name '*.avi' -o -name '*.mov'"
                elif media_type == "documents":
                    search_dir = os.path.expanduser("~/Documents")
                    ext_pattern = "-name '*.pdf' -o -name '*.doc' -o -name '*.docx' -o -name '*.txt'"
                else:
                    search_dir = os.path.expanduser("~")
                    ext_pattern = ""
                
                # Build and execute command
                cmd = f"find {search_dir} -type f \\( {ext_pattern} \\) -iname '*{query}*' | head -n 20"
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True
                )
                
                files = []
                for file_path in result.stdout.strip().split('\n'):
                    if file_path:
                        files.append({
                            'path': file_path,
                            'content': f"Media file found: {file_path}"
                        })
                
                return files
        except Exception as e:
            return {"error": str(e)}
    
    #-------------------------------------------------------------------
    # Windows App Operations (HexWin)
    #-------------------------------------------------------------------
    
    def list_windows_apps(self):
        """List all installed Windows applications"""
        try:
            if self.mcp:
                return self.mcp.list_windows_apps()
            else:
                return {"error": "Windows app listing not available without MCP client"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_windows_app(self, app_name_or_path):
        """Run a Windows application by name or path"""
        try:
            if not self.mcp:
                return {"error": "Windows app execution not available without MCP client"}
                
            # Check if this is a direct path
            if os.path.exists(app_name_or_path) and app_name_or_path.lower().endswith('.exe'):
                return self.mcp.run_windows_app(app_name_or_path)
            
            # Try to find the app by name
            apps = self.mcp.list_windows_apps()
            for app in apps:
                if app_name_or_path.lower() in app['name'].lower():
                    # Found the app
                    return self.mcp.run_windows_app(app['exe'])
            
            return {"error": f"Windows application '{app_name_or_path}' not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def install_windows_app(self, installer_path, app_name=None):
        """Install a Windows application"""
        try:
            if not self.mcp:
                return {"error": "Windows app installation not available without MCP client"}
                
            if app_name is None:
                # Extract name from installer path
                app_name = os.path.basename(installer_path).split('.')[0]
                
            return self.mcp.install_windows_app(installer_path, app_name)
        except Exception as e:
            return {"error": str(e)}
    
    #-------------------------------------------------------------------
    # Android App Operations (HexDroid)
    #-------------------------------------------------------------------
    
    def list_android_apps(self):
        """List all installed Android applications"""
        try:
            if self.mcp:
                return self.mcp.list_android_apps()
            else:
                return {"error": "Android app listing not available without MCP client"}
        except Exception as e:
            return {"error": str(e)}
    
    def install_android_app(self, apk_path, runtime=None):
        """Install an Android application"""
        try:
            if not self.mcp:
                return {"error": "Android app installation not available without MCP client"}
                
            return self.mcp.install_android_app(apk_path, runtime)
        except Exception as e:
            return {"error": str(e)}
    
    def launch_android_app(self, app_name):
        """Launch an Android application by name"""
        try:
            if not self.mcp:
                return {"error": "Android app launching not available without MCP client"}
                
            # Find the app by name
            apps = self.mcp.list_android_apps()
            found_app = None
            
            for app in apps:
                if app_name.lower() in app['name'].lower():
                    found_app = app
                    break
            
            if found_app:
                return self.mcp.launch_android_app(found_app['id'])
            else:
                return {"error": f"Android application '{app_name}' not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def uninstall_android_app(self, app_name):
        """Uninstall an Android application by name"""
        try:
            if not self.mcp:
                return {"error": "Android app uninstallation not available without MCP client"}
                
            # Find the app by name
            apps = self.mcp.list_android_apps()
            found_app = None
            
            for app in apps:
                if app_name.lower() in app['name'].lower():
                    found_app = app
                    break
            
            if found_app:
                return self.mcp.uninstall_android_app(found_app['id'])
            else:
                return {"error": f"Android application '{app_name}' not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_android_runtime_status(self):
        """Get status of Android runtimes"""
        try:
            if self.mcp:
                return self.mcp.get_android_runtime_status()
            else:
                return {"error": "Android runtime status not available without MCP client"}
        except Exception as e:
            return {"error": str(e)}
    
    #-------------------------------------------------------------------
    # System Application Operations
    #-------------------------------------------------------------------
    
    def list_native_apps(self):
        """List native Linux applications"""
        try:
            if self.mcp:
                # Use MCP to run command to list desktop files
                result = self.mcp.execute_command("find /usr/share/applications -name \"*.desktop\" -type f")
                if "error" in result:
                    return result
            else:
                # Fall back to local execution
                import subprocess
                result_obj = subprocess.run(
                    "find /usr/share/applications -name \"*.desktop\" -type f",
                    shell=True, capture_output=True, text=True
                )
                result = {"output": result_obj.stdout}
                
            desktop_files = result["output"].strip().split("\n")
            
            # Parse desktop files to get application names
            apps = []
            for desktop_file in desktop_files:
                try:
                    app_info = {}
                    with open(desktop_file, "r") as f:
                        content = f.read()
                        
                    # Extract application name
                    name_match = re.search(r"Name=(.*)", content)
                    if name_match:
                        app_info["name"] = name_match.group(1).strip()
                    else:
                        continue
                        
                    # Extract exec command
                    exec_match = re.search(r"Exec=(.*)", content)
                    if exec_match:
                        app_info["command"] = exec_match.group(1).strip().split(" ")[0]
                    else:
                        continue
                    
                    # Extract categories
                    category_match = re.search(r"Categories=(.*)", content)
                    if category_match:
                        app_info["categories"] = category_match.group(1).strip()
                    
                    # Include the desktop file path
                    app_info["desktop_file"] = desktop_file
                    
                    apps.append(app_info)
                except Exception as e:
                    # Skip failed desktop files
                    continue
            
            return {"apps": apps}
        except Exception as e:
            return {"error": str(e)}
    
    def launch_native_app(self, app_name):
        """Launch a native Linux application by name"""
        try:
            # Get all native apps
            apps_result = self.list_native_apps()
            
            if "error" in apps_result:
                return apps_result
                
            apps = apps_result.get("apps", [])
            
            # Find the app by name
            found_app = None
            for app in apps:
                if app_name.lower() in app["name"].lower():
                    found_app = app
                    break
            
            if found_app:
                # Launch the application
                if self.mcp:
                    return self.mcp.execute_command(found_app["command"])
                else:
                    # Fall back to local execution
                    import subprocess
                    result = subprocess.run(
                        f"{found_app['command']} &",
                        shell=True, capture_output=True, text=True
                    )
                    return {"success": result.returncode == 0, "message": f"Application {app_name} launched"}
            else:
                # Try directly launching by command
                if self.mcp:
                    return self.mcp.execute_command(app_name)
                else:
                    # Fall back to local execution
                    import subprocess
                    result = subprocess.run(
                        f"{app_name} &",
                        shell=True, capture_output=True, text=True
                    )
                    return {"success": result.returncode == 0, "message": f"Command {app_name} executed"}
        except Exception as e:
            return {"error": str(e)}
    
    #-------------------------------------------------------------------
    # New External Service Integrations
    #-------------------------------------------------------------------
    
    def search_with_rag(self, query):
        """Search using Trieve RAG"""
        if not self.capabilities.get('trieveRAG'):
            return {"error": "Trieve RAG capability not available"}
        
        try:
            # Get API key
            api_key = self.api_keys.get('trieve_api_key')
            
            # Set up Trieve API request
            url = "https://api.trieve.ai/api/chunk/search"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Use the default dataset ID or get from credentials
            dataset_id = self.api_keys.get('trieve_dataset_id', 'default')
            
            # Prepare search payload
            payload = {
                "query": query,
                "dataset_id": dataset_id,
                "search_type": "semantic",
                "page": 1,
                "limit": 10
            }
            
            # Make the request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Process and return results
            results = response.json()
            
            # Format results for display
            files = []
            for chunk in results.get('chunks', []):
                files.append({
                    'path': chunk.get('tracking_id', 'Unknown'),
                    'content': chunk.get('content', ''),
                    'score': chunk.get('score', 0)
                })
            
            return files
        
        except Exception as e:
            logger.error(f"Error searching with Trieve RAG: {e}")
            return {"error": f"Error searching with Trieve RAG: {str(e)}"}
    
    def research_topic(self, query):
        """Research a topic using Perplexity API"""
        if not self.capabilities.get('perplexityResearch'):
            return {"error": "Perplexity Research capability not available"}
        
        try:
            # Get API key - try both new and existing key names
            api_key = self.api_keys.get('perplexity_api_key') or self.api_keys.get('perplexity')
            if not api_key:
                return {"error": "Perplexity API key not found"}
            
            # Import OpenAI client
            try:
                from openai import OpenAI
            except ImportError:
                logger.error("OpenAI client library not installed. Please install with 'pip install openai'")
                return {"error": "OpenAI client library not installed. Please install with 'pip install openai'"}
            
            # Set up the client and messages
            client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a research assistant that provides accurate and helpful information."
                },
                {
                    "role": "user",
                    "content": f"Please research this topic thoroughly: {query}"
                }
            ]
            
            # Make the request (non-streaming)
            response = client.chat.completions.create(
                model="sonar-deep-research", # or "sonar-medium-online" or other available models
                messages=messages,
            )
            
            # Extract the content
            content = response.choices[0].message.content
            
            # Format as a structured result for display
            search_results = [{
                "title": f"Research: {query}",
                "content": content
            }]
            
            return {
                "source": "Perplexity Research",
                "results": search_results
            }
        
        except Exception as e:
            logger.error(f"Error researching with Perplexity: {e}")
            return {"error": f"Error researching with Perplexity: {str(e)}"}
    
    def search_web(self, query):
        """Search the web using SerpAPI"""
        if not self.capabilities.get('googleSearch'):
            return {"error": "Google Search capability not available"}
        
        try:
            # Get API key - try both new and existing key names
            api_key = self.api_keys.get('serpapi_api_key') or self.api_keys.get('serp')
            if not api_key:
                return {"error": "SerpAPI key not found"}
            
            # Set up SerpAPI request
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": "b2e1c812ba17a299010c054a8a0647a40cd92ff130e543a544a2dfa59951f114",
                "engine": "google"
            }
            
            # Make the request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Process and return results
            results = response.json()
            
            # Format search results for display
            search_results = []
            
            # Add organic results
            for result in results.get('organic_results', []):
                title = result.get('title', 'No Title')
                link = result.get('link', 'Unknown Link')
                snippet = result.get('snippet', 'No Description')
                
                search_results.append({
                    'title': title,
                    'url': link,
                    'content': snippet,
                })
            
            # Return in a format that works with the carousel
            return {
                "source": "Google Search",
                "results": search_results
            }
        
        except Exception as e:
            logger.error(f"Error searching the web with SerpAPI: {e}")
            return {"error": f"Error searching the web: {str(e)}"}
    
    def search_news(self, query):
        """Search news using NewsAPI"""
        if not self.capabilities.get('newsSearch'):
            return {"error": "News Search capability not available"}
        
        try:
            # Get API key
            api_key = self.api_keys.get('newsapi_api_key')
            
            # Set up NewsAPI request
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": api_key,
                "language": "en",
                "sortBy": "publishedAt"
            }
            
            # Make the request
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Process and return results
            results = response.json()
            
            # Format news results for display
            files = []
            for article in results.get('articles', []):
                files.append({
                    'path': article.get('url', 'Unknown URL'),
                    'content': f"{article.get('title', 'No Title')}\n\nSource: {article.get('source', {}).get('name', 'Unknown')}\nPublished: {article.get('publishedAt', 'Unknown')}\n\n{article.get('description', 'No Description')}"
                })
            
            return files
        
        except Exception as e:
            logger.error(f"Error searching news with NewsAPI: {e}")
            return {"error": f"Error searching news: {str(e)}"}
    
    #-------------------------------------------------------------------
    # Voice Command Processing
    #-------------------------------------------------------------------
    
    def process_voice_command(self, command_text):
        """Process a voice command to control the system"""
        command = command_text.lower()
        
        # Check for new research or search commands
        if command.lower().startswith(("find news", "search news")):
            query = command.split(" ", 2)[2]
            return {"response": f"Searching news for: {query}", "results": self.search_news(query)}
        
        elif command.lower().startswith(("search web", "search google")):
            query = command.split(" ", 2)[2]
            return {"response": f"Searching the web for: {query}", "results": self.search_web(query)}
        
        elif command.lower().startswith(("research", "deep research")):
            query = command.split(" ", 1)[1]
            return {"response": f"Researching topic: {query}", "results": self.research_topic(query)}
        
        elif command.lower().startswith(("use rag", "rag search")):
            query = command.split(" ", 2)[2]
            return {"response": f"Searching with RAG for: {query}", "results": self.search_with_rag(query)}
            
        # Check for app launch commands from original implementation
        app_launch_patterns = [
            r"open (.*)",
            r"launch (.*)",
            r"start (.*)",
            r"run (.*)"
        ]
        
        for pattern in app_launch_patterns:
            match = re.search(pattern, command)
            if match:
                app_name = match.group(1).strip()
                
                # Try launching as native app first
                result = self.launch_native_app(app_name)
                if not isinstance(result, dict) or "error" not in result:
                    return {"success": True, "action": "launch_native", "app": app_name}
                
                # Try as Windows app
                result = self.run_windows_app(app_name)
                if not isinstance(result, dict) or "error" not in result:
                    return {"success": True, "action": "launch_windows", "app": app_name}
                
                # Try as Android app
                result = self.launch_android_app(app_name)
                if not isinstance(result, dict) or "error" not in result:
                    return {"success": True, "action": "launch_android", "app": app_name}
                
                return {"error": f"Could not find application '{app_name}'"}
        
        # Check for file search commands
        file_search_patterns = [
            r"find (.*) files",
            r"search for (.*) files",
            r"locate (.*) files"
        ]
        
        for pattern in file_search_patterns:
            match = re.search(pattern, command)
            if match:
                query = match.group(1).strip()
                return self.search_files(query)
        
        # Check for media search commands
        media_patterns = {
            "images": [r"find (.*) images", r"search for (.*) pictures", r"show (.*) photos"],
            "videos": [r"find (.*) videos", r"search for (.*) movies", r"show (.*) videos"],
            "documents": [r"find (.*) documents", r"search for (.*) docs", r"show (.*) documents"]
        }
        
        for media_type, patterns in media_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    query = match.group(1).strip()
                    return self.find_media(query, media_type)
        
        # If command not recognized and perplexity is available, try that
        if self.capabilities.get('perplexityResearch'):
            return {"response": "Processing your question...", "results": self.research_topic(command)}
        
        # If no pattern matched, return error
        return {"error": "Command not recognized"}
        
# Main function for testing
if __name__ == "__main__":
    mcp_integration = MCPIntegration()
    
    # Test capabilities
    print("MCP Capabilities:")
    print(mcp_integration.capabilities)
    
    # Test Windows apps
    print("\nWindows Apps:")
    print(mcp_integration.list_windows_apps())
    
    # Test Android apps
    print("\nAndroid Apps:")
    print(mcp_integration.list_android_apps()) 