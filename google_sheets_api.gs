// Google Apps Script for Aswathama Classes - Student Data Management
// Deploy as a web app and use the URL in your Python Flask app

const SHEET_ID = "YOUR_SHEET_ID"; // Replace with your Sheet ID
const SHEET_NAME = "Students";

// Initialize sheet on first load
try {
  initializeSheet();
} catch (e) {
  console.log("Note: Initialize on first request: " + e);
}

function doGet(e) {
  initializeSheet();
  const action = e.parameter.action;
  
  try {
    switch(action) {
      case 'get_all':
        return ContentService.createTextOutput(
          JSON.stringify(getAllStudents())
        ).setMimeType(ContentService.MimeType.JSON);
      
      case 'get':
        return ContentService.createTextOutput(
          JSON.stringify(getStudent(e.parameter.id))
        ).setMimeType(ContentService.MimeType.JSON);
      
      default:
        return ContentService.createTextOutput(
          JSON.stringify({error: "Invalid action"})
        ).setMimeType(ContentService.MimeType.JSON);
    }
  } catch(error) {
    return ContentService.createTextOutput(
      JSON.stringify({error: error.toString()})
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  initializeSheet();
  const action = e.parameter.action;
  const data = JSON.parse(e.postData.contents);
  
  try {
    switch(action) {
      case 'add':
        addStudent(data);
        return ContentService.createTextOutput(
          JSON.stringify({success: true, message: "Student added"})
        ).setMimeType(ContentService.MimeType.JSON);
      
      case 'update':
        updateStudent(data.id, data);
        return ContentService.createTextOutput(
          JSON.stringify({success: true, message: "Student updated"})
        ).setMimeType(ContentService.MimeType.JSON);
      
      case 'delete':
        deleteStudent(data.id);
        return ContentService.createTextOutput(
          JSON.stringify({success: true, message: "Student deleted"})
        ).setMimeType(ContentService.MimeType.JSON);
      
      case 'authenticate':
        const result = authenticateStudent(data.id, data.password);
        return ContentService.createTextOutput(
          JSON.stringify(result)
        ).setMimeType(ContentService.MimeType.JSON);
      
      default:
        return ContentService.createTextOutput(
          JSON.stringify({error: "Invalid action"})
        ).setMimeType(ContentService.MimeType.JSON);
    }
  } catch(error) {
    return ContentService.createTextOutput(
      JSON.stringify({error: error.toString()})
    ).setMimeType(ContentService.MimeType.JSON);
  }
}

function getSheet() {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  return ss.getSheetByName(SHEET_NAME) || ss.getActiveSheet();
}

function getHeaders() {
  const sheet = getSheet();
  return sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
}

function findColumnIndex(header, headerRow) {
  return headerRow.indexOf(header) + 1;
}

function getAllStudents() {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const students = [];
  
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[0]) { // Check if ID exists
      students.push(rowToStudent(row, headers));
    }
  }
  return students;
}

function getStudent(id) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const idIndex = findColumnIndex('id', headers) - 1;
  
  for (let i = 1; i < data.length; i++) {
    if (data[i][idIndex] === id) {
      return rowToStudent(data[i], headers);
    }
  }
  return null;
}

function authenticateStudent(id, password) {
  const student = getStudent(id);
  if (student && student.password === password) {
    const result = {...student};
    delete result.password;
    return result;
  }
  return null;
}

function addStudent(data) {
  const sheet = getSheet();
  const headers = getHeaders();
  
  if (sheet.getLastRow() === 0) {
    // Add headers if sheet is empty
    sheet.appendRow(headers);
  }
  
  const row = headers.map(header => data[header] || '');
  
  // Handle JSON fields
  if (data.tests) row[findColumnIndex('tests_json', headers) - 1] = JSON.stringify(data.tests);
  if (data.attendance_log) row[findColumnIndex('attendance_log_json', headers) - 1] = JSON.stringify(data.attendance_log);
  if (data.progress) row[findColumnIndex('progress_json', headers) - 1] = JSON.stringify(data.progress);
  
  sheet.appendRow(row);
}

function updateStudent(id, data) {
  const sheet = getSheet();
  const sheetData = sheet.getDataRange().getValues();
  const headers = sheetData[0];
  const idIndex = findColumnIndex('id', headers) - 1;
  
  for (let i = 1; i < sheetData.length; i++) {
    if (sheetData[i][idIndex] === id) {
      const row = sheetData[i];
      
      // Update fields
      for (const key in data) {
        const colIndex = findColumnIndex(key, headers) - 1;
        if (colIndex >= 0) {
          if (typeof data[key] === 'object') {
            row[colIndex] = JSON.stringify(data[key]);
          } else {
            row[colIndex] = data[key];
          }
        }
      }
      
      sheet.getRange(i + 1, 1, 1, headers.length).setValues([row]);
      return;
    }
  }
}

function deleteStudent(id) {
  const sheet = getSheet();
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const idIndex = findColumnIndex('id', headers) - 1;
  
  for (let i = data.length - 1; i >= 1; i--) {
    if (data[i][idIndex] === id) {
      sheet.deleteRow(i + 1);
      return;
    }
  }
}

function rowToStudent(row, headers) {
  const student = {};
  const idIndex = findColumnIndex('id', headers) - 1;
  
  headers.forEach((header, index) => {
    if (header.includes('_json')) {
      const key = header.replace('_json', '');
      try {
        student[key] = row[index] ? JSON.parse(row[index]) : [];
      } catch (e) {
        student[key] = [];
      }
    } else {
      student[header] = row[index] || '';
    }
  });
  
  return student;
}

// Initialize sheet structure
function initializeSheet() {
  const sheet = getSheet();
  const lastRow = sheet.getLastRow();
  
  if (lastRow === 0) {
    const headers = [
      'id', 'name', 'password', 'email', 'phone', 'student_class', 
      'enrollment_date', 'tests_json', 'attendance_log_json', 'progress_json'
    ];
    sheet.appendRow(headers);
    Logger.log("Headers created: " + headers.join(", "));
  }
  
  return true;
}
