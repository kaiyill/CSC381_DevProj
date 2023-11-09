document.addEventListener('DOMContentLoaded', () => {
    const tableContainer = document.getElementById('table-container');
    const uploadForm = document.querySelector('form');
    const highDataPreferenceSelect = document.getElementById('highDataPreference');

    // Function to update the color scale based on user preference
    const updateColorScale = () => {
        const table = document.querySelector('.table');
        const headers = table.querySelectorAll('thead th');
        const highDataPreference = highDataPreferenceSelect.value;

        headers.forEach((header, columnIndex) => {
            const column = table.querySelectorAll(`tbody tr td:nth-child(${columnIndex + 1})`);
            const values = Array.from(column).map((cell) => parseFloat(cell.textContent));
            const max = Math.max(...values);
            const min = Math.min(...values);

            column.forEach((cell) => {
                const value = parseFloat(cell.textContent);
                if (!isNaN(value)) {
                    const colorScale = d3.scaleLinear()
                        .domain([min, (min + max) / 2, max])
                        .range(highDataPreference === 'good' ? ['red', 'gray', 'green'] : ['green', 'gray', 'red']);
                    const color = colorScale(value);
                    cell.style.backgroundColor = color;
                }
            });
        });
    };

    // Event listener for changes in the high data preference
    highDataPreferenceSelect.addEventListener('change', updateColorScale);

    // Event listener for form submission
    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(uploadForm);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            tableContainer.innerHTML = data.data;

            // Update the color scale based on the user's preference after table update
            updateColorScale();
        }
    });
});
