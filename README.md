# Report for Assignment 1

## Project chosen

Name: mypy

URL: https://github.com/python/mypy

Number of lines of code and the tool used to count it: 86.419 KLOC counted using lizard

Programming language: Python

## Coverage measurement

### Existing tool

<Inform the name of the existing tool that was executed and how it was executed>

Tool: Pytest-cov which uses coverage.py under the hood (it says coverage.py v7.3.2 in the screenshot)

Command: python -m pytest -q --cov mypy --cov-config .coveragerc --cov-report=term-missing --cov-report=html

<Show the coverage results provided by the existing tool with a screenshot>

![Screenshot 1](cov-before-ss1.png)
![Screenshot 2](cov-before-ss2.png)
![Screenshot 3](cov-before-ss3.png)
![Screenshot 4](cov-before-ss4.png)
![Screenshot 5](cov-before-ss5.png)

### Your own coverage tool

<The following is supposed to be repeated for each group member>

<Group member name> 

<Function 1 name> 

<Show a patch (diff) or a link to a commit made in your forked repository that shows the instrumented code to gather coverage measurements>

<Provide a screenshot of the coverage results output by the instrumentation>

<Function 2 name>

<Provide the same kind of information provided for Function 1>





Shane Prent (Goose-9 on Github)

Original function name: visit_deleted_type() in mypy/meet.py

Coverage tool implemented in mypy/meet_with_coverage.py as it allowed for a better printing system and code organisation. The function visit_deleted_type() in meet_with_coverage.py is a copy/overridden version of the same function in mypy/meet.py

https://github.com/python/mypy/commit/e63f6189d20e5663f18001252845db82c6a6c875

Coverage results output can also be seen in [test_visit_deleted_output.txt](test_visit_deleted_output.txt)

!["Output txt file when running visit_deleted_type()](visit_deleted_type_output.png))

Original function name: visit_type_var_tuple() in mypy/meet.py

Coverage tool implemented in mypy/meet_with_coverage.py as it again allowed for a better printing system and code organisation. The function visit_type_var_tuple() in meet_with_coverage.py is a copy/overridden version of the same function in mypy/meet.py

https://github.com/python/mypy/commit/e63f6189d20e5663f18001252845db82c6a6c875

Coverage results output can also be seen in [test_visit_var_tuple_output.txt](test_visit_var_tuple_output.txt)

!["Output txt file when running visit_type_var_tuple_output()](visit_type_var_tuple_output.png))

## Coverage improvement

### Individual tests

<The following is supposed to be repeated for each group member>

<Group member name>

<Test 1>

<Show a patch (diff) or a link to a commit made in your forked repository that shows the new/enhanced test>

<Provide a screenshot of the old coverage results (the same as you already showed above)>

<Provide a screenshot of the new coverage results>

<State the coverage improvement with a number and elaborate on why the coverage is improved>

<Test 2>

<Provide the same kind of information provided for Test 1>

### Overall

<Provide a screenshot of the old coverage results by running an existing tool (the same as you already showed above)>

<Provide a screenshot of the new coverage results by running the existing tool using all test modifications made by the group>

Command to run: python -m pytest -q --cov mypy --cov-config .coveragerc --cov-report=term-missing --cov-report=html

## Statement of individual contributions

<Write what each group member did>
