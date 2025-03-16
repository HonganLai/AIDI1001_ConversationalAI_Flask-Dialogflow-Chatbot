async function fetchStudentNumber() {
  try {
    const response = await fetch('/StudentNumber');
    
    if (!response.ok) {
      throw new Error('Failed to fetch student number');
    }

    const data = await response.json();

    if (data.student_number) {
      document.getElementById('student-number-display').textContent = data.student_number;
    } else {
      document.getElementById('student-number-display').textContent = 'Student number not found';
    }
  } catch (error) {
    console.error('Error:', error);

    document.getElementById('student-number-display').textContent = 'Error fetching student number';
  }
}

window.onload = fetchStudentNumber;
