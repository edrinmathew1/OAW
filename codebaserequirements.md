Project Title: Observable Agent Runtime

Project Description:

Observable Agent Runtime is a Python-based AI agent simulation system designed to demonstrate how modern intelligent agents process, plan, and execute user tasks. The project focuses on transparency and observability by allowing users to see which tool is selected for a given task and how the execution process takes place. Unlike traditional AI systems that operate as black boxes, this project provides a simplified view of the internal workflow of an agent-based architecture.

The system accepts user commands and routes them to specialized tools based on the task type. Each tool is responsible for a specific functionality such as information retrieval, memory management, or code execution. The agent acts as a central controller that analyzes user input, selects the appropriate tool, and manages the execution process. All actions are recorded in an execution log to maintain traceability and provide visibility into agent operations.

The project is designed using Object-Oriented Programming principles and demonstrates key concepts such as classes, objects, inheritance, abstract classes, abstract methods, polymorphism, encapsulation, and file handling. It serves as an introductory implementation of an AI agent runtime and provides a foundation for future enhancements such as real web search integration, tool chaining, memory systems, API connectivity, and advanced AI models.

Domain:
Artificial Intelligence and Agent Systems

Objectives:

* To simulate the workflow of an AI-powered agent system.
* To demonstrate core Object-Oriented Programming concepts in Python.
* To implement task routing using specialized tools.
* To provide transparent execution through logging and observability.
* To create a modular architecture that can be extended with additional tools and AI capabilities.

Modules:

1. Agent Controller Module

* Acts as the central coordinator of the system.
* Receives user tasks.
* Selects the appropriate tool based on task type.
* Manages execution flow.
* Maintains execution history.

2. Web Search Tool Module

* Handles search-related requests.
* Simulates retrieval of information from online resources.
* Demonstrates specialized tool behavior.

3. Memory Management Module

* Stores user notes and information.
* Retrieves previously saved memories.
* Uses file handling for persistent storage.

4. Code Execution Tool Module

* Processes code-related requests.
* Simulates execution of programming tasks.
* Represents interaction between AI agents and development tools.

5. Execution Logging Module

* Records executed tasks.
* Stores timestamps and tool usage history.
* Provides transparency and observability.

6. User Interaction Module

* Accepts commands from the user.
* Displays tool outputs.
* Provides access to memory records and execution logs.

Key Features:

* AI agent simulation.
* Task routing and planning.
* Tool-based architecture.
* Memory storage and retrieval.
* Execution history tracking.
* Interactive command-line interface.
* Modular and extensible design.

OOP Concepts Implemented:

1. Class and Object

* Multiple classes are created to represent the agent and its tools.
* Objects are instantiated from these classes and used during execution.

2. Inheritance

* Tool classes inherit from a common parent class called AgentTool.

3. Abstract Class and Abstract Method

* AgentTool is implemented as an abstract class.
* The execute() method is defined as an abstract method and implemented differently by each tool.

4. Polymorphism

* Different tool objects are stored and handled through a common interface.
* The same execute() method produces different behavior depending on the tool being used.

5. Encapsulation

* Each tool manages its own internal functionality and data independently.

Future Scope:

* Integration with Large Language Models (LLMs).
* Real web search capabilities.
* Tool chaining and multi-step task execution.
* Database-backed memory storage.
* FastAPI-based backend services.
* Real-time execution dashboard.
* Multi-agent collaboration.
* Web-based user interface.
* Voice command support.
* Advanced agent planning and reasoning.



#1
Requirements
1.Class and Object
Create at least one base class and instantiate multiple objects.
Include suitable attributes and methods.
2. Inheritance
Create at least two derived classes that inherit from a common parent class.
3. Abstract Class and Abstract Method
Define an abstract class with at least one abstract method.
Implement the abstract method differently in each derived class.
4. Polymorphism
Store objects of different derived classes in a collection (list/array).
Invoke the same method on all objects and demonstrate different behaviors.

#2
Design and develop a Login and Registration System for a real-world application domain of your choice (e.g., Hospital Management System, Banking System, Library Management System, Student Management System, E-Commerce System, Hotel Booking System, Employee Management System, etc.).

The system must validate all user inputs using Python's Regular Expressions (re module) and handle invalid inputs using Exception Handling mechanisms.

Objectives

The application should:
Accept user information through Login and Registration forms.
Validate user inputs using Regular Expressions.
Handle all possible input errors gracefully using Exception Handling.
Demonstrate the use of all major Regular Expression functions available in Python. (search(), match(), fullmatch(), findall(), split(), compile(), sub())
Display meaningful error messages to users.

#3
Design and develop a GUI-based application using PyQt for a domain of your choice. The application should allow users to enter data, validate the input, process the information, and display the validated results using appropriate widgets and dialogue boxes.

Your application must satisfy the following requirements:

Design a user-friendly graphical interface using a minimum of four (4) different layout managers.
Use a minimum of five (5) different PyQt widgets to collect, display, and manage user input.
Implement appropriate input validation to ensure that only valid data is accepted.
Use signals and slots to handle user interactions, with at least five (5) signal-slot connections.
Implement a minimum of three (3) event handling methods (such as keyboard, mouse, window, or focus events) that perform meaningful actions within the application.
Display appropriate success, warning, and error messages using dialog boxes or suitable GUI widgets.
Provide options to submit, clear/reset, and exit the application, with appropriate confirmation where necessary.

#4
Fetch data from a public API, process JSON response, and display meaningful information.
Use appropriate dictionary functions to process Json file. Make an efficient and meaningful program

#5
 Data Exchange using JSON, HTTP Methods, Status Codes, Error Handling
 Create a JSON dataset containing at least 10 records relevant to the selected domain.
Develop a simple Web API using Flask (or any suitable Python framework) to provide access to the JSON data through appropriate URL endpoints.
Implement and demonstrate the following HTTP methods:
GET – Retrieve one or more records.
POST – Add a new record.
PUT – Update an existing record.
DELETE – Remove a record.
Write a Python client program using the requests library to consume the developed Web API.
Exchange data between the client and server in JSON format.
Parse the JSON response and display the retrieved information in a user-friendly format.
Implement basic error handling to handle invalid URLs, unavailable resources, invalid requests, connection failures, and appropriate HTTP status codes

#6
streamlit application.

#7
File Handling
Implement separate user-defined functions to perform the following operations:
o Create a file and store records.
o Read and display all records.
o Append new records.
o Search for a record using a suitable key.
o Update an existing record.
o Delete a record.
o Create a backup copy of the data file.
File Opening Modes
Demonstrate the use of appropriate file opening modes such as:
o w
o r
o a
o r+
o w+
 File Handling Methods
Use suitable file handling methods wherever applicable, such as:
o read()
o readline()
o readlines()
o write()
o writelines()
o seek()
o tell()

o close()
 Input Validation
Validate user inputs using Regular Expressions wherever applicable (e.g., ID, email address,
phone number, date, password, product code, vehicle number, etc.).
 Graphical User Interface
Develop the application using either Streamlit or PyQt with an appropriate user interface for
data entry, search, update, and display.
 Programming Requirements
o Use user-defined functions.
o Implement appropriate exception handling.
o Display meaningful success and error messages.
o Organize the program using modular programming practices.


