<div align="center">
  <h1>Council Management System</h1>
  <p>
    A system customized specifically for private university council for their management and reporting needs
  </p>
  <p>
    Built using RESTFul Django (Server) Backend and Vue based Frontend (Web Interface).
  </p>
</div>


## Getting the backend working on your machine for development [First Time Setup]:
1. Download the corresponding version of python on your machine  ```[Currently Python v3.10].``` 
2. Install pipenv package globally by running the following command ```pip install pipenv``` in any terminal/CMD window.
3. Clone the project to your desired directory on your machine.
4. Navigate to the directory of that project, and open a terminal/cmd window with the backend directory.
5. Run the following command ```pipenv install``` to install the project dependancies.
6. Make sure there is an ```.env``` file in the backend directory, if there is skip step 7.
7. Run the following command ```pipenv run setenv dev``` to create a ```.env``` file with the development parameters.
8. Now to start the server run the command  ```pipenv run start```
9. Happy coding.

- These steps are a one time setup, after getting everything running first time, you just need to run ```pipenv run start``` when you need to start the server.

### [For VSCode Users] Getting intellisense working in the backend
1. You must have the python extension installed.
2. After doing the steps above for the first time, press ```ctrl + shift + P```, then type in ```>python: Select Interpreter``.
3. Select the backend interpreter that has the word pipenv.
4. This will allow vscode's intellisense to work correctly.
5. Happy coding.

## Getting the frontend working on your machine for development [First Time Setup]:
1. Download the corresponding version of node on your machine  ```[Currently Node v16.14.2].``` 
2. Clone the project to your desired directory on your machine.
3. Navigate to the directory of that project, and open a terminal/cmd window with the frontend directory.
4. Run the following command ```npm install``` to install the project dependancies.
5. Make sure there is an ```.env``` file in the front directory, if there is skip step 7.
6. Run the following command ```npm run setenv dev``` to create a ```.env``` file with the development parameters.
7. Now to start the server run the command  ```npm start``` or ```npm run dev```
8. Happy coding.

- These steps are a one time setup, after getting everything running first time, you just need to run ```npm start``` or ```npm run dev``` when you need to start the server.

### [For VSCode Users] Getting intellisense working in the frontend
1. You should install the extentions volar and vscode-typescript-vue-plugin
2. This will allow vscode's intellisense to work correctly with vue and typescript.
3. Happy coding.
