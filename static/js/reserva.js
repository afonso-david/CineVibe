let currentStep = 1;
let selectedQuantity = 1;
let selectedSeats = [];
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 Sistema iniciado');
    console.log('📊 Dados:', movieData);
    console.log('🪑 Lugares:', seatsData.length);
    generateSeating();
});
function changeQty(delta) {
    const newQty = selectedQuantity + delta;
    if (newQty >= 1 && newQty <= 8) {
        selectedQuantity = newQty;
        document.getElementById('qty').value = selectedQuantity;
        if (selectedSeats.length > selectedQuantity) {
            const excess = selectedSeats.slice(selectedQuantity);
            excess.forEach(seatId => {
                const seat = document.querySelector(`[data-seat="${seatId}"]`);
                if (seat) seat.classList.remove('selected');
            });
            selectedSeats = selectedSeats.slice(0, selectedQuantity);
            updateUI();
        }
    }
}
function nextStep() {
    if (currentStep === 2 && selectedSeats.length !== selectedQuantity) {
        alert(`Selecione ${selectedQuantity} lugar(es)`);
        return;
    }
    if (currentStep < 3) {
        currentStep++;
        updateSteps();
    }
}
function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateSteps();
    }
}
function updateSteps() {
    document.querySelectorAll('.step').forEach((step, i) => {
        step.classList.toggle('active', i + 1 === currentStep);
    });
    document.querySelectorAll('.step-content').forEach((content, i) => {
        content.classList.toggle('active', i + 1 === currentStep);
    });
    if (currentStep === 3) {
        updateSummary();
    }
}
Gerar planta do cinema - 12 fileiras
function generateSeating() {
    const container = document.getElementById('seating');
    const capacity = movieData.sala.capacidade;
    const rows = 12;
    const seatsPerRow = Math.ceil(capacity / rows);
    const rowLabels = 'ABCDEFGHIJKL';
    console.log(`📐 Layout: ${rows} fileiras x ${seatsPerRow} lugares`);
    for (let r = 0; r < rows; r++) {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'row';
        const label = document.createElement('div');
        label.className = 'row-label';
        label.textContent = rowLabels[r];
        rowDiv.appendChild(label);
        const leftSeats = document.createElement('div');
        leftSeats.className = 'seats';
        const leftCount = Math.floor(seatsPerRow / 2);
        for (let s = 1; s <= leftCount; s++) {
            const seat = createSeat(rowLabels[r], s);
            leftSeats.appendChild(seat);
        }
        rowDiv.appendChild(leftSeats);
        const aisle = document.createElement('div');
        aisle.className = 'aisle';
        rowDiv.appendChild(aisle);
        const rightSeats = document.createElement('div');
        rightSeats.className = 'seats';
        for (let s = leftCount + 1; s <= seatsPerRow; s++) {
            const seat = createSeat(rowLabels[r], s);
            rightSeats.appendChild(seat);
        }
        rowDiv.appendChild(rightSeats);
        container.appendChild(rowDiv);
    }
}
function createSeat(row, num) {
    const seatId = `${row}${num}`;
    const seatData = seatsData.find(s => s.nome_lugar === seatId);
    const seat = document.createElement('div');
    seat.className = 'seat';
    seat.dataset.seat = seatId;
    seat.title = `Lugar ${seatId}`;
    if (seatData && seatData.ocupado) {
        seat.classList.add('taken');
    } else {
        seat.classList.add('free');
        seat.addEventListener('click', () => toggleSeat(seat, seatId));
    }
    return seat;
}
oggle seleção de lugar
function toggleSeat(seat, seatId) {
    if (seat.classList.contains('selected')) {
        seat.classList.remove('selected');
        seat.classList.add('free');
        selectedSeats = selectedSeats.filter(id => id !== seatId);
    } else {
        if (selectedSeats.length >= selectedQuantity) {
            alert(`Pode selecionar apenas ${selectedQuantity} lugar(es)`);
            return;
        }
        seat.classList.remove('free');
        seat.classList.add('selected');
        selectedSeats.push(seatId);
    }
    updateUI();
}
function updateUI() {
    const continueBtn = document.getElementById('continueBtn');
    if (continueBtn) {
        continueBtn.disabled = selectedSeats.length !== selectedQuantity;
    }
}
function updateSummary() {
    document.getElementById('selectedSeats').textContent = 
        selectedSeats.length > 0 ? selectedSeats.join(', ') : '-';
    const total = selectedSeats.length * movieData.price;
    document.getElementById('totalPrice').textContent = `€${total.toFixed(2)}`;
}
async function confirmBooking() {
    if (selectedSeats.length === 0) {
        alert('Selecione pelo menos um lugar');
        return;
    }
    const bookingData = {
        sessao_id: sessionId,
        data_sessao: movieData.date || new Date().toISOString().split('T')[0],
        lugares: selectedSeats,
        quantidade: selectedSeats.length,
        preco_total: selectedSeats.length * movieData.price
    };
    try {
        const response = await fetch('/confirmar_reserva', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookingData)
        });
        const result = await response.json();
        if (result.success) {
            alert('Reserva confirmada!');
            window.location.href = '/';
        } else {
            alert(`Erro: ${result.message}`);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro interno. Tente novamente.');
    }
}