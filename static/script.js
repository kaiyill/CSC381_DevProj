document.addEventListener('DOMContentLoaded', () => {
    const tableContainer = document.getElementById('table-container');
    const uploadForm = document.querySelector('form');

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

            // Add a three-color gradient scale: red for bad, gray for in-between, and green for good
            const table = document.querySelector('.table');
            const headers = table.querySelectorAll('thead th');
            const highDataPreference = document.getElementById('highDataPreference').value;

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
                            .range(['red', 'gray', 'green']);
                        const color = colorScale(value);
                        cell.style.backgroundColor = color;
                    }
                });
            });
        }
    });
});

