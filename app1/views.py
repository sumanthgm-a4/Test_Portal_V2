import io
import os
import sys
import json
import pytest
import tempfile
import traceback
import subprocess
from collections import OrderedDict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import *

# Create your views here.

def render_home(request):
    return render(request, "index.html")

def render_login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('home')
    if request.method == "POST":
        a = request.POST.get("username")
        b = request.POST.get("password")
        auth = authenticate(request, username=a, password=b)
        if auth:
            login(request, auth)
            return redirect('home')
        else:
            messages.error(request, "Please enter correct login credentials")
            return render(request, "login.html")
    return render(request, "login.html")

def render_register(request):
    if request.method == "POST":
        firstname = request.POST.get('fname')
        lastname = request.POST.get('lname')
        email = request.POST.get('mailid')
        username = request.POST.get('username')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email already exists")
            return redirect('register')
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists")
            return redirect('register')
        if len(password) < 8:
            messages.error(request, "Password must have 8 or more characters")
            return redirect('register')
        if password.isalnum():
            messages.error(request, "Password must have at least one special character")
            return redirect('register')
        if password != cpassword:
            messages.error(request, "Passwords don't match")
            return redirect('register')
        
        new_user = User(username=username, first_name=firstname, last_name=lastname, email=email)
        new_user.set_password(password)
        new_user.save()
        messages.success(request, "User successfully created")
        return redirect('login')
    return render(request, "register.html")

@login_required
def render_logout(request):
    logout(request)
    messages.info(request, "You are successfully logged out")
    return redirect('login')

@login_required
def render_test_page(request, question_name):
    question = TestQuestion.objects.get(question_name=question_name)
    num = len(question.visible_test_cases)
    
    return render(request, "test.html", {'question': question, 'num': num})

# @csrf_exempt
# def run_code(request):
#     if request.method == "POST":
#         # Parse incoming JSON data for the 'code' field
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#             code = data.get('code', None)  # Get 'code' from JSON payload

#             if not code:
#                 return JsonResponse({'error': 'No code provided'}, status=400)

#             # Test cases
#             test_cases = [
#                 {'input': 5, 'expected': 120},
#                 {'input': 3, 'expected': 6},
#                 {'input': 10, 'expected': 3628800},
#                 {'input': 0, 'expected': 1},
#                 {'input': 1, 'expected': 1},
#                 {'input': 2, 'expected': 2},
#                 {'input': 15, 'expected': 1307674368000},
#             ]

#             failed_test_count = 0
#             results = f''

#             for test_case in test_cases:
#                 input_value = test_case['input']
#                 expected_output = test_case['expected']

#                 print(code)
                
#                 # Prepare the code to include the solve_factorial function
#                 code_with_input = f"""
# def solve_factorial(n):
#     # User-provided function code goes here
#     {code}

# # Now we run the solve_factorial function with the input_value
# print(solve_factorial({input_value}))
#                 """

#                 print(code_with_input)
                
#                 # Execute the code in a separate process
#                 code_output = execute_code(code_with_input)
#                 if code_output != str(expected_output):
#                     failed_test_count += 1
#                 if test_case['input'] == 5 or test_case['input'] == 3:
#                     results += f"\nInput: {test_case['input']}\nOutput: {code_output.rstrip()}\nExpected: {expected_output}\n\n"
#                 print("RESULTS:", results)

#             return JsonResponse({
#                 'output': f"Test Results: {results}",
#                 'error': None,
#                 'failed_count': failed_test_count
#             })

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON format'}, status=400)

# def execute_code(code):
#     try:
#         # Execute the code in a subprocess and capture the output
#         process = subprocess.Popen(
#             ['python3', '-c', code],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )

#         # Get the output from the process
#         stdout, stderr = process.communicate()

#         # Log the output for debugging
#         print("STDOUT: ", stdout.decode('utf-8'))  # This will log the actual output
#         print("STDERR: ", stderr.decode('utf-8'))  # This will log any errors

#         if stderr:
#             return f"Error: {stderr.decode('utf-8')}"

#         return stdout.decode('utf-8').strip()
#     except Exception as e:
#         return f"Error: {str(e)}"


# @csrf_exempt
# def run_code(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         code = data.get("code")
#         question_name = data.get("question_name")  # Use question name for lookup

#         # Fetch the question from the database
#         try:
#             question = TestQuestion.objects.get(question_name=question_name)
#         except TestQuestion.DoesNotExist:
#             return JsonResponse({"error": "Question not found"}, status=404)

#         # Test cases
#         visible_test_cases = question.visible_test_cases
#         hidden_test_cases = question.hidden_test_cases

#         # Function to run the code (sandboxed and simple example)
#         def run_test(input_data, expected_output):
#             local_scope = {}
#             try:
#                 exec(code, {}, local_scope)  # Run user code in a sandboxed scope
#                 func = local_scope.get("solution")  # Ensure user defines a function named "solution"
#                 if func:
#                     result = func(*map(int, input_data.split(",")))  # Pass test case input
#                     return str(result) == expected_output
#             except Exception as e:
#                 return False  # If any error occurs, consider the test failed

#         # Validate visible test cases
#         visible_passed = sum(
#             run_test(tc["input"], tc["output"]) for tc in visible_test_cases
#         )

#         # Validate hidden test cases
#         hidden_passed = sum(
#             run_test(tc["input"], tc["output"]) for tc in hidden_test_cases
#         )

#         # Response
#         return JsonResponse({
#             "visible_passed": visible_passed,
#             "visible_total": len(visible_test_cases),
#             "hidden_passed": hidden_passed,
#             "hidden_total": len(hidden_test_cases),
#         })

#     return JsonResponse({"error": "Invalid request"}, status=400)


from django.http import JsonResponse
import json
from .models import TestQuestion
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def run_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        code = data.get("code")
        question_name = data.get("question_name")  # Use question_name here to fetch the question

        # Fetch the question from the database using question_name
        try:
            question = TestQuestion.objects.get(question_name=question_name)
        except TestQuestion.DoesNotExist:
            return JsonResponse({"error": "Question not found"}, status=404)

        # Test cases
        visible_test_cases = question.visible_test_cases
        hidden_test_cases = question.hidden_test_cases

        # Function to run the code (sandboxed and simple example)
        def run_test(input_data, expected_output):
            local_scope = {}
            try:
                exec(code, {}, local_scope)  # Run user code in a sandboxed scope
                func = local_scope.get("solution")  # Ensure user defines a function named "solution"
                if func:
                    result = func(*map(int, input_data.split(",")))  # Pass test case input
                    return str(result) == expected_output
            except Exception as e:
                return False  # If any error occurs, consider the test failed

        # Validate visible test cases
        visible_passed = sum(
            run_test(tc["input"], tc["output"]) for tc in visible_test_cases
        )

        # Validate hidden test cases
        hidden_passed = sum(
            run_test(tc["input"], tc["output"]) for tc in hidden_test_cases
        )

        # Return the results as a JSON response
        return JsonResponse({
            "visible_passed": visible_passed,
            "visible_total": len(visible_test_cases),
            "hidden_passed": hidden_passed,
            "hidden_total": len(hidden_test_cases),
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def render_questions(request):
    questions = TestQuestion.objects.all()
    if questions:
        print(questions[0]._id)
        print(questions[0].question_name)
    
    return render(request, 'questions.html', {'questions': questions})


def delete_question(request, question_name):
    question = TestQuestion.objects.get(question_name=question_name)
    question.delete()
    return redirect('questions')


def add_question(request):
    if request.method == 'POST':
        question_name = request.POST.get('question_name')
        question_desc = request.POST.get('question_desc')
        visible_test_cases = request.POST.get('visible_test_cases')
        hidden_test_cases = request.POST.get('hidden_test_cases')

        # Parse the test cases from the JSON input
        try:
            visible_test_cases = json.loads(visible_test_cases)
            hidden_test_cases = json.loads(hidden_test_cases)
        except json.JSONDecodeError:
            return render(request, 'add_question.html', {'error': 'Invalid JSON format for test cases.'})

        # Create and save the question to MongoDB
        TestQuestion.objects.create(
            question_name=question_name,
            question_desc=question_desc,
            visible_test_cases=visible_test_cases,
            hidden_test_cases=hidden_test_cases
        )

        # Redirect to a success page or question list page
        return redirect('questions')  # You can change this to whatever view you want

    return render(request, 'add_question.html')



def run_user_code(request):
    if request.method == "POST":
        try:
            # Parse the incoming request data
            data = json.loads(request.body)
            user_code = data.get("code")
            question_name = data.get("question_name")  # Retrieve question by name

            # Retrieve the question from the database by its unique name
            question = TestQuestion.objects.get(question_name=question_name)

            # Test case evaluation function
            def evaluate_code(code, test_cases):
                passed_cases = 0
                results = []

                for case in test_cases:
                    try:
                        # Run user code in a secure subprocess
                        process = subprocess.run(
                            ["python3", "-c", code],
                            input=case["input"],
                            text=True,
                            capture_output=True,
                            timeout=5  # Prevent infinite loops
                        )

                        # Compare output with the expected output
                        if process.stdout.strip() == case["output"].strip():
                            passed_cases += 1
                            results.append({"input": case["input"], "output": process.stdout.strip(), "status": "Passed"})
                        else:
                            results.append({"input": case["input"], "output": process.stdout.strip(), "status": "Failed"})

                    except subprocess.TimeoutExpired:
                        results.append({"input": case["input"], "output": "", "status": "Timeout"})
                    except Exception as e:
                        results.append({"input": case["input"], "output": str(e), "status": "Error"})

                return passed_cases, results

            # Evaluate user code for visible and hidden test cases
            visible_passed, visible_results = evaluate_code(user_code, question.visible_test_cases)
            hidden_passed, hidden_results = evaluate_code(user_code, question.hidden_test_cases)

            # Prepare the response
            response_data = {
                "visible_case_results": visible_results,
                "visible_passed": visible_passed,
                "visible_total": len(question.visible_test_cases),
                "hidden_passed": hidden_passed,
                "hidden_total": len(question.hidden_test_cases),
            }

            return JsonResponse(response_data)

        except TestQuestion.DoesNotExist:
            return JsonResponse({"error": "Question not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)