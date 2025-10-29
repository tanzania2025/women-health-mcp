"""
CLI application interface for DoctHER.
"""

import asyncio
import sys
from typing import Optional
from .cli_chat import CliChat


class CliApp:
    """Command line interface application for DoctHER."""
    
    def __init__(self, chat: CliChat):
        self.chat = chat
        self.running = True
    
    async def initialize(self):
        """Initialize the CLI application."""
        print("🔬 DoctHER: AI-Powered Women's Health Assistant")
        print("=" * 50)
        print("Initializing medical research tools...")
        
        try:
            # Test connection to MCP server
            tools = await self.chat.doc_client.list_tools()
            print(f"✅ Connected! Available tools: {len(tools)}")
            for tool in tools[:5]:  # Show first 5 tools
                print(f"   - {tool.name}: {tool.description[:60]}...")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
            print()
        except Exception as e:
            print(f"❌ Error connecting to MCP server: {e}")
            print("Make sure the MCP server is running.")
            sys.exit(1)
    
    async def run(self):
        """Run the CLI application."""
        print("Ready! Ask me about women's health, fertility, or reproductive medicine.")
        print("Type 'quit', 'exit', or press Ctrl+C to quit.")
        print("Type 'clear' to clear conversation history.")
        print("-" * 50)
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n🩺 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Thank you for using DoctHER! Stay healthy!")
                    break
                
                if user_input.lower() == 'clear':
                    self.chat.clear_history()
                    print("🧹 Conversation history cleared.")
                    continue
                
                if user_input.lower() == 'help':
                    await self.show_help()
                    continue
                
                # Process the message
                print("\n🤔 DoctHER is thinking...")
                response = await self.chat.process_message(user_input)
                
                print(f"\n🩺 DoctHER: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Thank you for using DoctHER! Stay healthy!")
                break
            except EOFError:
                print("\n\n👋 Thank you for using DoctHER! Stay healthy!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.")
    
    async def show_help(self):
        """Show help information."""
        print("\n📚 DoctHER Help")
        print("-" * 30)
        print("Available commands:")
        print("  help  - Show this help message")
        print("  clear - Clear conversation history")
        print("  quit  - Exit the application")
        print("  exit  - Exit the application")
        print("\nI can help with:")
        print("• Fertility and reproductive health questions")
        print("• IVF success rate calculations")
        print("• Clinical guideline searches (ESHRE, NAMS, ASRM)")
        print("• PubMed research literature")
        print("• Menopause and hormone therapy")
        print("• Research data from longitudinal studies")
        print("\nExample questions:")
        print('• "What are the ESHRE guidelines for PCOS treatment?"')
        print('• "Calculate IVF success for a 35-year-old with AMH 2.5"')
        print('• "Find recent research on menopause hormone therapy"')
        print('• "What are NAMS recommendations for hot flashes?"')