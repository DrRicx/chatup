# Project Setup

In order for the project to fully function you must follow the following set of instruction that will discuss when
reading the contents of the of documentation below. Since the project is run on Django web framework it is expected for
you to create a virtual env after cloning the repository

In this part you will learn how to setup the project from cloning and running it from your localhost.

## Before you start

You must have the following requirements:

Make sure that you have:

- MySQL workbench
- good internet connection

## Cloning the repository

In the first part of the project setup, clone the following url An absolute link
to [ChatUP](https://github.com/DrRicx/chatup) in your terminal.

1. Execute the following command in the terminal:

   ```bash
    git clone https://github.com/DrRicx/chatup
   ```

2. After cloning the repository the contents of the project should show in your current folder

## Creating and Activating the Virtual ENV

In the second part of the setup, you must create a virtual environment inside the cloned repository to run the project.

1. Change directory to go inside the cloned repository, to be precised our current project

   ```bash
    cd chatup
   ```

2. Inside our project, create a virtual environment by executing the following command:

   ```bash
    python -m venv .venv
   ```
3. Activate your current virtual environment by going inside the folder and selecting activate or activate.bat
   ```bash
    cd .venv/Scripts/activate
   ```
   or
   ```bash
   cd .venv/Scripts/activate.bat
   ```
   
   If you are inside pycharm make sure that the current virtual environment is your environment. You can see it by searching interpreter in the settings.

   <img alt="img.png" src="img.png"/>

   >Make sure the interpreter is the name of the folder where the project is currently saved in, in this case the project is saved in the folder name "chatup".
   {style="note"}

   <img alt="img_1.png" src="img_1.png"/>
   

<seealso>
<!--Give some related links to how-to articles-->
</seealso>
