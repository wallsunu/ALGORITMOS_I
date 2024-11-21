document.addEventListener('DOMContentLoaded', () => {
    const recetas = [
        { nombre: 'Sándwich de pollo con zanahorias', calorias: 497 },
        { nombre: 'Pollo a la Mostaza y Orégano', calorias: null },
        { nombre: 'Sándwich de Pollo con Zanahoria y Espinaca', calorias: 797 }
    ];

    const recetasDiv = document.getElementById('recetas');
    recetas.forEach(receta => {
        const recetaDiv = document.createElement('div');
        recetaDiv.className = 'receta';
        recetaDiv.innerHTML = `<h2>${receta.nombre}</h2><p>${receta.calorias ? receta.calorias + ' kcal' : 'Calorías no disponibles'}</p>`;
        recetasDiv.appendChild(recetaDiv);
    });
});