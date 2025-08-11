
$(document).on("click", "#scrollToForm", function (e) {
  e.preventDefault();
  document.getElementById("formSection").scrollIntoView({ behavior: "smooth" });
});


let fName = "";
let lName = "";
let workoutPlan = [];

$(document).on("click", "#final_formSubmit", function (e) {
  e.preventDefault();


  fName = $("#firstName").val();
  lName = $("#lastName").val();
  const height = $("#height").val();
  const weight = $("#weight").val();
  const duration = $("#duration").val();
  const days = $("#days").val();
  const ageGroup = $('input[name="ageGroup"]:checked').val();
  const gender = $('input[name="gender"]:checked').val();
  const goal = $('input[name="goal"]:checked').val();
  const level = $('input[name="level"]:checked').val();
  const location = $('input[name="location"]:checked').val();

  let targetMuscles = [];
  $('input[name="muscles[]"]:checked').each(function () {
    targetMuscles.push($(this).val());
  });

    if (!validateWorkoutForm(fName, lName, height, weight, duration, days, ageGroup, gender, goal, level, location, targetMuscles)) {
        return;
    }

    
  $("#loader").fadeIn(200);
  $("#formSection").fadeOut(200);

  $("#workout-container").empty();

  const userData = {
    firstName: fName,
    lastName: lName,
    height: height,
    weight: weight,
    duration: duration,
    days: days,
    ageGroup: ageGroup,
    gender: gender,
    goal: goal,
    level: level,
    location: location,
    muscles: targetMuscles.join(","),
  };

  $.ajax({
    url: "http://localhost:5000/api/workout-plan",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify(userData),
    success: function (response) {
      $("#loader").fadeOut(200);

      workoutPlan = Array.isArray(response.workout_plans)
        ? response.workout_plans
        : [];

      if (workoutPlan.length === 0) {
        $("#workout-container").html(
          "<p>Error: Invalid or empty workout plan returned.</p>"
        );
        $("#final_formSubmit").fadeIn(200); 
        return;
      }

      $("#planOutput").fadeIn(400);

      $("#workout-container").html(`
        <div class="pdf-ready-message" style="text-align: center; padding: 2rem;">
            <h3 style="font-size: 1.5rem; margin-bottom: 1rem;">🎉 Your personalized ShyFit workout plan is ready!</h3>
            <button id="downloadPdfBtn" style="background-color: #5a67d8; color: #fff; padding: 1rem 2rem; font-size: 1.1rem; border: none; border-radius: 8px; cursor: pointer;">
            Download My Plan
            </button>
        </div>
        `);
    },
    error: function (xhr, status, error) {
      $("#loader").fadeOut(200);
      console.error("API Error:", status, error);
      $("#workout-container").html("<p>Failed to load workout plan.</p>");
      $("#final_formSubmit").fadeIn(200);
    },
  });
});

$("html, body").animate(
  {
    scrollTop: $("#planOutput").offset().top,
  },
  500
);
$(document).on("click", "#downloadPdfBtn", function () {
 const { jsPDF } = window.jspdf;
const doc = new jsPDF({ unit: "mm", format: "a4" });

// Title block
doc.setFont("helvetica", "bold");
doc.setFontSize(20);
doc.setTextColor(40, 40, 40);
doc.text(`ShyFit Workout Plan`, 105, 20, { align: "center" });

doc.setFontSize(12);
doc.setTextColor(80, 80, 80);
doc.text(`For: ${fName} ${lName}`, 105, 28, { align: "center" });

// Reserve vertical space after title
let yOffset = 40; // Start AFTER title

// Loop through each workout day
workoutPlan.forEach((day, index) => {
  // Start new page after Day 1
  if (index !== 0) {
    doc.addPage();
    yOffset = 20;
  }

  // Section Header
  doc.setFontSize(14);
  doc.setTextColor(30, 30, 120);
  doc.setFont("helvetica", "bold");
  doc.text(`Day ${index + 1}: ${day.name || "Workout"}`, 14, yOffset);
  yOffset += 8;

  // Meta Info
  doc.setFontSize(10);
  doc.setTextColor(70, 70, 70);
  doc.setFont("helvetica", "normal");
  doc.text(`Goal: ${day.goal || "N/A"} | Duration: ${day.duration_minutes || "N/A"} mins | Calories: ${day.estimated_calories || "N/A"}`, 14, yOffset);
  yOffset += 6;
  doc.text(`Equipment: ${day.equipment || "None"} | Muscles: ${(day.target_muscles || []).join(", ")}`, 14, yOffset);
  yOffset += 6;

  // Table
  if ((day.exercises || []).length > 0) {
    doc.autoTable({
      startY: yOffset,
      margin: { left: 14 },
      head: [[
        'Exercise',
        'Sets',
        'Reps / Duration',
        'Rest (sec)',
        'Description'
      ]],
      body: (day.exercises || []).map((ex) => {
        const repOrDuration = ex.reps !== undefined
          ? `${ex.reps} reps`
          : ex.duration_seconds
          ? `${ex.duration_seconds} secs`
          : "N/A";
        return [
          ex.name,
          ex.sets || '-',
          repOrDuration,
          ex.rest || '-',
          ex.description || ''
        ];
      }),
      styles: {
        fontSize: 10,
        cellPadding: 4,
        textColor: [40, 40, 40],
        halign: 'left',
        valign: 'middle',
      },
      headStyles: {
        fillColor: [245, 245, 245],
        textColor: [0, 0, 0],
        fontStyle: 'bold',
        halign: 'center',
        lineWidth: 0.2,
        lineColor: [180, 180, 180],
      },
      bodyStyles: {
        lineWidth: 0.1,
        lineColor: [200, 200, 200],
        minCellHeight: 12,
      },
      alternateRowStyles: {
        fillColor: [250, 250, 250],
      },
      columnStyles: {
        0: { cellWidth: 45 },
        1: { cellWidth: 15 },
        2: { cellWidth: 25 },
        3: { cellWidth: 20 },
        4: { cellWidth: 70 },
      },
      theme: 'grid',
    });

    yOffset = doc.lastAutoTable.finalY + 10;
  }
});
  const fileName = `ShyFit_for_${fName}_${lName}.pdf`;
  doc.save(fileName);
});

document.addEventListener("DOMContentLoaded", function () {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
});




 function validateWorkoutForm(fName, lName, height, weight, duration, days, ageGroup, gender, goal, level, location, targetMuscles) {
  let isValid = true;
  $(".required-message").hide();
  if (!fName || fName.trim() === "") {
    $("#firstNameError").show();
    isValid = false;
  }
  if (!lName || lName.trim() === "") {
    $("#lastNameError").show();
    isValid = false;
  }
  if (!height || height.trim() === "") {
    $("#heightError").show();
    isValid = false;
  }
  if (!weight || weight.trim() === "") {
    $("#weightError").show();
    isValid = false;
  }
  if (!duration || duration.trim() === "") {
    $("#durationError").show();
    isValid = false;
  }
  if (!days || days.trim() === "") {
    $("#daysError").show();
    isValid = false;
  }
  if (!ageGroup) {
    $("#ageError").show();
    isValid = false;
  }
  if (!gender) {
    $("#genderError").show();
    isValid = false;
  }
  if (!goal) {
    $("#goalError").show();
    isValid = false;
  }
  if (!level) {
    $("#levelError").show();
    isValid = false;
  }
  if (!location) {
    $("#locationError").show();
    isValid = false;
  }
  if (!targetMuscles || targetMuscles.length === 0) {
    $("#fullbodyError").show();
    isValid = false;
  }

  return isValid;
}


$(document).on("input", "input[type='text'], input[type='number']", function () {
  const inputId = $(this).attr("id");
  $(`#${inputId}Error`).hide();
});

$(document).on("change", "input[type='radio']", function () {
  const name = $(this).attr("name");
  const value = $(this).val();
  const id = $(this).attr("id");

  switch (name) {
    case "ageGroup":
      $("#ageError").hide();
      break;
    case "gender":
      $("#genderError").hide();
      break;
    case "goal":
      $("#goalError").hide();
      break;
    case "level":
      $("#levelError").hide();
      break;
    case "location":
      $("#locationError").hide();
      break;
  }

 if (name === 'goal') {
  if (id === 'goal-fatloss' || id === 'goal-flexibility' || id === 'goal-endurance') {
    $("#fullbody").prop("checked", true);
    $("input[name='muscles[]']").not("#fullbody").prop("checked", false).prop("disabled", true);
  } else {
    $("input[name='muscles[]']").prop("disabled", false);
  }
}

});

$(document).on("change", "input[name='muscles[]']", function () {
  const id = $(this).attr("id");

  const fullBody = $("#fullbody");
  const others = $("input[name='muscles[]']").not("#fullbody");

  // 1. If "Full Body" is selected, uncheck others
  if (id === 'fullbody' && $(this).is(":checked")) {
    others.prop("checked", false);
    return;
  }

  // 2. If any other is selected, uncheck "Full Body"
  if (id !== 'fullbody' && $(this).is(":checked")) {
    fullBody.prop("checked", false);
  }

  // 3. If all others are selected, auto-select "Full Body" and uncheck others
  const allOthersChecked = others.length === others.filter(":checked").length;

  if (allOthersChecked) {
    fullBody.prop("checked", true);
    others.prop("checked", false);
  }
});


$(document).on("input", "#duration", function () {
  const value = parseInt($(this).val(), 10);
  if (value > 24) {
    $("#durationLimitError").show();
  } else {
    $("#durationLimitError").hide();
  }

  if(value < 1){
    $("#ZeroDurationLimitError").show();
  }else{
    $("#ZeroDurationLimitError").hide();
  }

  if (value > 0) {
    $("#durationError").hide();
  }
});

$(document).on("input", "#days", function () {
  const value = parseInt($(this).val(), 10);
  if (value > 7) {
    $("#daysLimitError").show();
  } else {
    $("#daysLimitError").hide();
  }

    if(value < 1){
        $("#ZeroDaysLimitError").show();
    }else{
        $("#ZeroDaysLimitError").hide();
    }
  

  if (value > 0) {
    $("#daysError").hide();
  }
});

