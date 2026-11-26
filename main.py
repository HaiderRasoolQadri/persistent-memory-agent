from agent import PersistentMemoryAgent


def main():
    print("=" * 50)
    print("Persistent Memory Agent")
    print("Type 'quit' to exit, 'facts' to see stored facts")
    print("=" * 50)

    agent = PersistentMemoryAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Goodbye!")
            break

        if user_input.lower() == "facts":
            facts = agent.semantic.get_all_facts()
            print("\nStored facts:")
            for k, v in facts.items():
                print(f"  - {k}: {v}")
            continue

        response = agent.chat(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()