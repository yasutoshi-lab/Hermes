#!/usr/bin/env python3
"""
Interactive chat bot example using ModelManager.

This example demonstrates multi-turn conversations with message history.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.model_manager import ModelManager, OllamaConnectionError


class ChatBot:
    """Simple chat bot using ModelManager."""

    def __init__(self, model_name: str, language: str = 'en'):
        """
        Initialize chat bot.

        Args:
            model_name: Name of the Ollama model to use
            language: Language for system prompt ('ja' or 'en')
        """
        self.manager = ModelManager()
        self.model_name = model_name
        self.language = language
        self.conversation = []

        # Set system message
        system_prompt = self.manager.get_system_prompt(language, 'general')
        self.conversation.append({
            "role": "system",
            "content": system_prompt
        })

        print(f"Chat bot initialized with {model_name}")
        print(f"Language: {language}")
        print(f"System prompt: {system_prompt}\n")

    def chat(self, user_message: str) -> str:
        """
        Send a message and get response.

        Args:
            user_message: User's message

        Returns:
            Bot's response
        """
        # Add user message to history
        self.conversation.append({
            "role": "user",
            "content": user_message
        })

        # Get response from model
        response = self.manager.chat(
            model_name=self.model_name,
            messages=self.conversation,
            temperature=0.7,
            max_tokens=500
        )

        # Add assistant response to history
        self.conversation.append({
            "role": "assistant",
            "content": response
        })

        return response

    def reset(self):
        """Reset conversation history."""
        system_msg = self.conversation[0]
        self.conversation = [system_msg]
        print("Conversation reset.\n")


def main():
    """Run interactive chat bot."""
    print("=" * 60)
    print("ModelManager: Interactive Chat Bot")
    print("=" * 60)

    # Initialize
    try:
        manager = ModelManager()
    except OllamaConnectionError as e:
        print(f"✗ Error: {e}")
        print("  Make sure Ollama is running!")
        return 1

    # Get model
    models = manager.list_models()
    if not models:
        print("No models available.")
        return 1

    model_name = models[0]
    print(f"Available models: {', '.join(models)}")

    # Choose language
    print("\nChoose language:")
    print("  1. English")
    print("  2. Japanese (日本語)")
    choice = input("Enter choice (1 or 2): ").strip()

    language = 'ja' if choice == '2' else 'en'

    # Create chat bot
    bot = ChatBot(model_name, language)

    # Instructions
    print("\n" + "=" * 60)
    print("Chat Bot Ready!")
    print("=" * 60)
    print("Commands:")
    print("  /reset  - Reset conversation")
    print("  /quit   - Exit chat bot")
    print("  /help   - Show this help")
    print("=" * 60)

    # Chat loop
    while True:
        try:
            # Get user input
            if language == 'ja':
                user_input = input("\nあなた: ").strip()
            else:
                user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()

                if command == '/quit':
                    print("Goodbye!")
                    break
                elif command == '/reset':
                    bot.reset()
                    continue
                elif command == '/help':
                    print("\nCommands:")
                    print("  /reset - Reset conversation")
                    print("  /quit  - Exit")
                    print("  /help  - Show help")
                    continue
                else:
                    print(f"Unknown command: {user_input}")
                    continue

            # Get response
            if language == 'ja':
                print("Bot: ", end='', flush=True)
            else:
                print("Bot: ", end='', flush=True)

            response = bot.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Use /quit to exit properly.")
            continue
        except Exception as e:
            print(f"\nError: {e}")
            continue

    return 0


if __name__ == "__main__":
    sys.exit(main())
