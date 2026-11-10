function startWorkout() {
    const type = document.getElementById('workoutType').value;
    const place = document.getElementById('workoutPlace').value;
  
    // Create the URL based on the combination
    const url = `${type}-${place}.html`;
  
    // Redirect to the corresponding page
    window.location.href = url;
  }
  