# Tasks: Multimodal Mindmap Agent

**Feature Name**: Multimodal Mindmap Agent

## Phase 1: Setup

- [X] T001 Create the `agente_imagem` directory and its `__init__.py` file.
- [X] T002 Create the `tests` directory and its `__init__.py` file.
- [X] T003 Create the `agente_imagem/main.py` file.
- [X] T004 Create the `tests/test_agente_imagem.py` file.
- [X] T005 Update `requirements.txt` with `langgraph`, `google-generativeai`, `python-dotenv`, `langchain-google-genai`, `Pillow`, `pytesseract`.
- [X] T006 Create a `.env` file in the project root, replicating the structure from `agente_simples`.

## Phase 2: Foundational

- [X] T007 Implement image loading and base64 encoding utility functions in `agente_imagem/utils.py`.
- [X] T008 Implement error handling for unclear/unreadable images and non-mind map images (log and terminate) in `agente_imagem/main.py`.

## Phase 3: User Story 1 - Analyze Mind Map Image

- [X] T009 [US1] Implement the core multimodal agent logic in `agente_imagem/main.py` to receive `folder_map.png`.
- [X] T010 [US1] Integrate `langchain-google-genai` to send the image and prompt to `gemini-2.5-flash` using `HumanMessage` in `agente_imagem/main.py`.
- [X] T011 [US1] Implement the logic to extract hierarchical structure (node text and level) from the model's response in `agente_imagem/main.py`.
- [X] T012 [US1] Implement the conversion of the extracted structure into a hierarchical markdown string in `agente_imagem/main.py`.
- [ ] T013 [US1] Add a test case in `tests/test_agente_imagem.py` to verify the agent processes a valid `folder_map.png` and returns a well-structured hierarchical markdown.
- [ ] T014 [US1] Add test cases in `tests/test_agente_imagem.py` for error handling of unclear/unreadable images and non-mind map images.

## Final Phase: Polish & Cross-Cutting Concerns

- [X] T015 Review and refine code for readability, maintainability, and adherence to Python standards in `agente_imagem/`.
- [X] T016 Ensure all dependencies are correctly listed in `requirements.txt`.
- [X] T017 Update `agente_imagem/README.md` with instructions on how to run the agent and expected output.

## Dependencies

- Phase 1 (Setup) -> Phase 2 (Foundational) -> Phase 3 (User Story 1) -> Final Phase (Polish)

## Parallel Execution Examples

- **User Story 1**:
    - T009, T010, T011, T012 can be developed in parallel if the interfaces between them are well-defined.
    - T013 and T014 can be developed in parallel.

## Implementation Strategy

- MVP first, focusing on User Story 1. Incremental delivery of features.