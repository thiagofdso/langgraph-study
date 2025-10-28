# Data Model for Router Persona Agent

## Entities

### User Input
- **Description**: Represents the initial message from the user, containing their age and a question.
- **Attributes**:
    - `age` (int): The age of the user.
    - `question` (str): The question posed by the user.

### Router Agent
- **Description**: The central component responsible for processing `User Input` and routing the conversation to the appropriate persona agent.
- **State/Logic**:
    - Determines if the `age` in `User Input` is <= 30 (young) or > 30 (non-young).
    - Directs messages to either the `Informal Agent` or `Formal Agent`.

### Informal Agent
- **Description**: Responds to young users with a communication style featuring emojis and informal language.
- **Behavior**:
    - Receives messages from the `Router Agent`.
    - Generates responses tailored for young users.

### Formal Agent
- **Description**: Responds to non-young users with a communication style that is serious and cordial.
- **Behavior**:
    - Receives messages from the `Router Agent`.
    - Generates responses tailored for non-young users.
