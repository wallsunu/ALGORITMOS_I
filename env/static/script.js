document.getElementById('weightForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevenir el comportamiento por defecto del formulario

    // Obtener valores del formulario
    const currentWeight = document.getElementById('currentWeight').value;
    const targetWeight = document.getElementById('targetWeight').value;

    // Mostrar los pesos en la sección de información
    document.getElementById('displayCurrentWeight').textContent = currentWeight;
    document.getElementById('displayTargetWeight').textContent = targetWeight;

    // Mostrar la información
    document.getElementById('weightInfo').style.display = 'block';
});
