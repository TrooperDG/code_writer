from langgraph.types import Command

from agent.graph import graph


def main():
    user_request = input("What code should I create?\n> ")

    initial_state = {
        "user_request": user_request,
        "generated_code": "",
        "code_approved": False,
    }

    config = {"configurable": {"thread_id": "coding-session-1"}}

    result = graph.invoke(
        initial_state,
        config=config,
    )

    print("\nGraph paused.")
    print(result["__interrupt__"])

    decision = input("\nApprove code? (yes/no): ").strip().lower()

    approved = decision == "yes"

    result = graph.invoke(
        Command(resume=approved),
        config=config,
    )

    print("\nFinal state:")
    print(result)


if __name__ == "__main__":
    main()
