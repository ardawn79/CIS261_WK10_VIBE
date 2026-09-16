#Ardawn Rodgers
#CIS261
#WK10 VIBE Coding - Student Grade Calculator


"""Student record manager with score and letter-grade calculations."""

import json
from dataclasses import dataclass
from pathlib import Path


DATA_FILE = Path(__file__).with_name("student_grades.txt")


def calculate_grade(average: float) -> str:
	"""Return a letter grade for an average score."""
	if average >= 90:
		return "A"
	if average >= 80:
		return "B"
	if average >= 70:
		return "C"
	if average >= 60:
		return "D"
	return "F"


@dataclass
class Student:
	name: str
	student_id: str
	scores: list[float]

	def __post_init__(self) -> None:
		self.name = self.name.strip()
		self.student_id = self.student_id.strip()
		self.scores = [float(score) for score in self.scores]
		if not self.name or not self.student_id:
			raise ValueError("Name and student ID are required.")
		if len(self.scores) != 5:
			raise ValueError("Exactly five test scores are required.")
		if any(score < 0 or score > 100 for score in self.scores):
			raise ValueError("Scores must be between 0 and 100.")

	@property
	def average(self) -> float:
		return round(sum(self.scores) / len(self.scores), 2)

	@property
	def id(self) -> str:
		return self.student_id

	@property
	def grade(self) -> str:
		return calculate_grade(self.average)

	def to_dict(self) -> dict:
		return {
			"name": self.name,
			"student_id": self.student_id,
			"scores": self.scores,
		}


class StudentRecords:
	"""Load, find, add, and save student records."""

	def __init__(self, file_path: Path = DATA_FILE) -> None:
		self.file_path = Path(file_path)
		self.students: list[Student] = []
		try:
			self.load()
		except (OSError, ValueError, json.JSONDecodeError) as error:
			print(f"Unable to load student records: {error}")
			self.students = []

	def load(self) -> None:
		if not self.file_path.exists():
			self.students = []
			return

		contents = self.file_path.read_text().strip()
		if not contents:
			self.students = []
		elif contents.startswith("["):
			self.students = [Student(**record) for record in json.loads(contents)]
		else:
			self.students = []
			for line_number, line in enumerate(contents.splitlines(), start=1):
				fields = line.split("|")
				if len(fields) != 9:
					raise ValueError(f"Invalid student record on line {line_number}.")
				self.students.append(
					Student(fields[0], fields[1], [float(score) for score in fields[2:7]])
				)

	def save(self) -> None:
		lines = [
			"|".join(
				[
					student.name,
					student.id,
					*(f"{score:.2f}" for score in student.scores),
					f"{student.average:.2f}",
					student.grade,
				]
			)
			for student in self.students
		]
		try:
			self.file_path.write_text("\n".join(lines) + ("\n" if lines else ""))
		except OSError as error:
			raise OSError(f"Unable to save student records: {error}") from error

	def find(self, student_id: str) -> Student | None:
		return next(
			(student for student in self.students if student.student_id == student_id),
			None,
		)

	def search_by_name(self, name: str) -> list[Student]:
		name = name.strip().casefold()
		return [student for student in self.students if name in student.name.casefold()]

	def add(self, student: Student) -> None:
		if self.find(student.student_id):
			raise ValueError("That student ID already exists.")
		self.students.append(student)

def read_input(prompt: str) -> str:
	"""Read input and treat the ESC character as an exit request."""
	value = input(prompt)
	if "\x1b" in value:
		raise EOFError
	return value.strip()


def format_score(score: float) -> str:
	return f"{score:.2f}"


def display_table(students: list[Student]) -> None:
	if not students:
		print("No student records found.")
		return

	headings = ["Name", "Student ID", "Test 1", "Test 2", "Test 3", "Test 4", "Test 5", "Average", "Grade"]
	rows = [
		[
			student.name,
			student.student_id,
			*(format_score(score) for score in student.scores),
			format_score(student.average),
			student.grade,
		]
		for student in students
	]
	widths = [max(len(str(value)) for value in column) for column in zip(headings, *rows)]
	separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
	print(separator)
	print("| " + " | ".join(f"{heading:<{width}}" for heading, width in zip(headings, widths)) + " |")
	print(separator)
	for row in rows:
		print("| " + " | ".join(f"{value:<{width}}" for value, width in zip(row, widths)) + " |")
	print(separator)


def display_statistics(students: list[Student]) -> None:
	if not students:
		print("No student records found.")
		return
	averages = [student.average for student in students]
	print(f"Highest average: {max(averages):.2f}")
	print(f"Lowest average: {min(averages):.2f}")
	print(f"Class average: {sum(averages) / len(averages):.2f}")


def add_student(records: StudentRecords) -> None:
	name = read_input("Name: ")
	student_id = read_input("Student ID: ")
	scores = [float(read_input(f"Test {number} score: ")) for number in range(1, 6)]
	records.add(Student(name, student_id, scores))
	records.save()
	print("Student added and saved successfully.")


def main() -> None:
	records = StudentRecords()
	while True:
		print("\nStudent Grade Manager")
		print("1. Add student")
		print("2. Display all students")
		print("3. Display class statistics")
		print("4. Search student by name")
		print("Press ESC to exit")

		try:
			choice = read_input("Choose an option: ")
			if choice == "1":
				add_student(records)
			elif choice == "2":
				display_table(records.students)
			elif choice == "3":
				display_statistics(records.students)
			elif choice == "4":
				matches = records.search_by_name(read_input("Name to search: "))
				display_table(matches)
			else:
				print("Please choose 1, 2, 3, or 4.")
		except EOFError:
			try:
				records.save()
				print("\nRecords saved. Goodbye!")
			except OSError as error:
				print(f"\nUnable to save records before exit: {error}")
			return
		except (OSError, ValueError, json.JSONDecodeError) as error:
			print(f"Error: {error}")


if __name__ == "__main__":
	main()