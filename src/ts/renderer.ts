const grid: HTMLElement | null = document.getElementById("grid");
const wordleHeight = 6;
const wordleWidth = 5;
function renderGrid() {
	if (grid) {
		for (let i = 0; i < wordleHeight; ++i) {
			const row = document.createElement("div");
			row.classList.add("gridRow");
			for (let j = 0; j < wordleWidth; ++j) {
				const cell = document.createElement("div");
				cell.classList.add("gridCell");
				row.appendChild(cell);
			}
			grid.appendChild(row);
		}
	}
}
document.addEventListener("DOMContentLoaded", renderGrid);
