class PatternVisualizer {
    constructor(containerId, patternData) {
        this.container = document.getElementById(containerId);
        this.pattern = patternData;
        this.scale = 0.1;
        this.init();
    }

    init() {
        this.container.innerHTML = '';
        const svg = this.createSVG();
        this.container.appendChild(svg);
        this.drawPattern();
    }

    createSVG() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '800');
        svg.setAttribute('height', '600');
        svg.setAttribute('viewBox', '0 0 800 600');
        svg.style.border = '1px solid #ccc';
        return svg;
    }

    drawPattern() {
        const svg = this.container.querySelector('svg');
        const mainPiece = this.pattern.pieces[0];
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', '50');
        rect.setAttribute('y', '50');
        rect.setAttribute('width', mainPiece.width * this.scale);
        rect.setAttribute('height', mainPiece.height * this.scale);
        rect.setAttribute('fill', '#e8f4f8');
        rect.setAttribute('stroke', '#333');
        rect.setAttribute('stroke-width', '2');
        svg.appendChild(rect);
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', 50 + (mainPiece.width * this.scale) / 2);
        label.setAttribute('y', 30);
        label.setAttribute('text-anchor', 'middle');
        label.textContent = 'Main Tube Body';
        svg.appendChild(label);
        this.pattern.pieces.slice(1).forEach((piece, index) => {
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', 50 + (index * 200));
            rect.setAttribute('y', 50 + piece.position.y * this.scale);
            rect.setAttribute('width', piece.width * this.scale);
            rect.setAttribute('height', piece.height * this.scale);
            rect.setAttribute('fill', '#ffeb3b');
            rect.setAttribute('stroke', '#333');
            rect.setAttribute('stroke-width', '2');
            svg.appendChild(rect);
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', 50 + (index * 200) + (piece.width * this.scale) / 2);
            label.setAttribute('y', 50 + piece.position.y * this.scale - 10);
            label.setAttribute('text-anchor', 'middle');
            label.textContent = `Reinforcement ${index + 1}`;
            svg.appendChild(label);
        });
        this.addDimensions(svg);
    }

    addDimensions(svg) {
        const mainPiece = this.pattern.pieces[0];
        const widthLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        widthLine.setAttribute('x1', '50');
        widthLine.setAttribute('y1', 50 + mainPiece.height * this.scale + 20);
        widthLine.setAttribute('x2', 50 + mainPiece.width * this.scale);
        widthLine.setAttribute('y2', 50 + mainPiece.height * this.scale + 20);
        widthLine.setAttribute('stroke', '#666');
        widthLine.setAttribute('stroke-width', '1');
        svg.appendChild(widthLine);
        const widthText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        widthText.setAttribute('x', 50 + (mainPiece.width * this.scale) / 2);
        widthText.setAttribute('y', 50 + mainPiece.height * this.scale + 35);
        widthText.setAttribute('text-anchor', 'middle');
        widthText.setAttribute('font-size', '12');
        widthText.textContent = `${mainPiece.width.toFixed(1)}mm`;
        svg.appendChild(widthText);
    }
}
