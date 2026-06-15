from matcher import calculate_similarity_and_match

jd = "We are looking for a backend developer experienced with Python, FastAPI, and PostgreSQL to build scalable APIs."
resume1 = "Senior Developer with 5 years of experience using Python, Django, and PostgreSQL. Familiar with REST APIs and AWS."
resume2 = "Frontend Engineer specializing in React, HTML, CSS, and Javascript. Built several user-facing apps."

print("--- Test Resume 1 ---")
result1 = calculate_similarity_and_match(jd, resume1)
print(result1)

print("\n--- Test Resume 2 ---")
result2 = calculate_similarity_and_match(jd, resume2)
print(result2)
