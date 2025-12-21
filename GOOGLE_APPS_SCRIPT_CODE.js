/**
 * ASWATHAMA CLASSES - Google Apps Script for Attendance Management
 * 
 * Instructions:
 * 1. Go to your Google Sheet
 * 2. Click Extensions → Apps Script
 * 3. Delete existing code and paste this entire script
 * 4. Click Deploy → New Deployment → Type: Web app
 * 5. Execute as: Your account
 * 6. Who has access: Anyone
 * 7. Copy the deployment URL
 * 8. Add to Replit Secrets: GOOGLE_APPS_SCRIPT_URL = your_deployment_url
 */

// Initialize sheet structure when first run
function initializeSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const classes = ['Class 8', 'Class 9', 'Class 10'];
  
  classes.forEach(className => {
    let sheet = ss.getSheetByName(className);
    if (!sheet) {
      sheet = ss.insertSheet(className);
      const headers = [['Roll No', 'Student Name', 'Date', 'Status', 'Notes']];
      sheet.getRange(1, 1, 1, 5).setValues(headers);
      sheet.setFrozenRows(1);
    }
  });
}

// Main doPost handler - receives requests from Flask
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action;
    
    switch(action) {
      case 'add_student':
        return addStudent(data);
      case 'get_students':
        return getStudents(data);
      case 'delete_student':
        return deleteStudent(data);
      case 'submit_attendance':
        return submitAttendance(data);
      case 'get_attendance':
        return getAttendance(data);
      case 'init':
        initializeSheets();
        return success({message: 'Sheets initialized'});
      default:
        return error('Unknown action: ' + action);
    }
  } catch(err) {
    return error(err.toString());
  }
}

function addStudent(data) {
  const {className, rollNo, name} = data;
  const sheet = getOrCreateSheet(className);
  
  const lastRow = sheet.getLastRow();
  const nextRow = lastRow + 1;
  
  sheet.getRange(nextRow, 1, 1, 2).setValues([[rollNo, name]]);
  
  return success({
    message: 'Student added successfully',
    student: {roll_no: rollNo, name: name}
  });
}

function getStudents(data) {
  const {className} = data;
  const sheet = getOrCreateSheet(className);
  
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    return success({students: []});
  }
  
  const values = sheet.getRange(2, 1, lastRow - 1, 2).getValues();
  const students = values.map(row => ({
    id: Utilities.getUuid(),
    roll_no: row[0],
    name: row[1],
    class: className
  }));
  
  return success({students: students});
}

function deleteStudent(data) {
  const {className, rollNo} = data;
  const sheet = getOrCreateSheet(className);
  
  const lastRow = sheet.getLastRow();
  for (let i = 2; i <= lastRow; i++) {
    if (sheet.getRange(i, 1).getValue().toString() === rollNo.toString()) {
      sheet.deleteRow(i);
      return success({message: 'Student deleted'});
    }
  }
  
  return error('Student not found');
}

function submitAttendance(data) {
  const {className, date, records} = data;
  const sheet = getOrCreateSheet(className);
  
  const lastRow = sheet.getLastRow();
  
  // Update attendance for each record
  records.forEach(record => {
    const studentId = record.student_id;
    
    // Find student by roll number (records should have this)
    for (let i = 2; i <= lastRow; i++) {
      const rollNo = sheet.getRange(i, 1).getValue();
      
      // Update date, status, notes
      sheet.getRange(i, 3).setValue(date);
      sheet.getRange(i, 4).setValue(record.status || '');
      sheet.getRange(i, 5).setValue(record.notes || '');
    }
  });
  
  return success({message: 'Attendance submitted successfully'});
}

function getAttendance(data) {
  const {className, date} = data;
  const sheet = getOrCreateSheet(className);
  
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    return success({records: []});
  }
  
  const values = sheet.getRange(2, 1, lastRow - 1, 5).getValues();
  const records = values
    .filter(row => !date || row[2].toString() === date)
    .map(row => ({
      roll_no: row[0],
      student_name: row[1],
      date: row[2],
      status: row[3],
      notes: row[4]
    }));
  
  return success({records: records});
}

function getOrCreateSheet(className) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(className);
  
  if (!sheet) {
    sheet = ss.insertSheet(className);
    const headers = [['Roll No', 'Student Name', 'Date', 'Status', 'Notes']];
    sheet.getRange(1, 1, 1, 5).setValues(headers);
  }
  
  return sheet;
}

function success(data) {
  return ContentService.createTextOutput(JSON.stringify({
    success: true,
    ...data
  })).setMimeType(ContentService.MimeType.JSON);
}

function error(message) {
  return ContentService.createTextOutput(JSON.stringify({
    success: false,
    message: message
  })).setMimeType(ContentService.MimeType.JSON);
}

// Test function (optional - run from Apps Script editor)
function testAddStudent() {
  const result = addStudent({
    className: 'Class 8',
    rollNo: '1',
    name: 'Test Student'
  });
}
