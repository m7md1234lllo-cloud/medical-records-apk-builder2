let participatingDoctorsCount = 0;
const doctorsList = {{ doctors|tojson }};

function addParticipatingDoctor() {
    participatingDoctorsCount++;
    const container = document.getElementById('participatingDoctorsList');
    
    const doctorCard = document.createElement('div');
    doctorCard.className = 'participating-doctor-card';
    doctorCard.id = `doctor-card-${participatingDoctorsCount}`;
    doctorCard.style.cssText = `
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        position: relative;
        animation: slideIn 0.3s ease;
    `;
    
    let doctorOptions = '<option value="">-- اختر طبيب --</option>';
    doctorsList.forEach(doc => {
        doctorOptions += `<option value="${doc.id}">د. ${doc.name}${doc.specialization ? ' - ' + doc.specialization : ''}</option>`;
    });
    
    doctorCard.innerHTML = `
        <button type="button" class="btn btn-danger btn-small" 
                style="position: absolute; top: 10px; left: 10px; padding: 0.5rem 1rem; z-index: 10;"
                onclick="removeParticipatingDoctor(${participatingDoctorsCount})">
            ✕ حذف
        </button>
        
        <div class="form-row" style="margin-top: 2rem;">
            <div class="form-group">
                <label>الطبيب</label>
                <select class="participating-doctor-select" data-index="${participatingDoctorsCount}" required>
                    ${doctorOptions}
                </select>
            </div>
            
            <div class="form-group">
                <label>الدور / المهمة</label>
                <div class="input-with-voice">
                    <input type="text" class="participating-doctor-role" id="role-${participatingDoctorsCount}" data-index="${participatingDoctorsCount}" 
                           placeholder="مثال: جراح مساعد، طبيب تخدير، استشاري">
                    <button type="button" class="voice-btn" data-target="role-${participatingDoctorsCount}">🎤</button>
                </div>
            </div>
        </div>
        
        <div class="form-group">
            <label>ملاحظات (اختياري)</label>
            <div class="input-with-voice">
                <textarea class="participating-doctor-notes" id="notes-${participatingDoctorsCount}" data-index="${participatingDoctorsCount}" 
                          rows="2" placeholder="أي ملاحظات خاصة بمشاركة هذا الطبيب"></textarea>
                <button type="button" class="voice-btn" data-target="notes-${participatingDoctorsCount}">🎤</button>
            </div>
        </div>
    `;
    
    container.appendChild(doctorCard);
    
    // Reinitialize voice buttons
    if (window.VoiceInput) {
        window.VoiceInput.attachToButtons();
    }
}

function removeParticipatingDoctor(index) {
    const card = document.getElementById(`doctor-card-${index}`);
    if (card) {
        card.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => card.remove(), 300);
    }
}

function getParticipatingDoctors() {
    const participating = [];
    const cards = document.querySelectorAll('.participating-doctor-card');
    
    cards.forEach(card => {
        const select = card.querySelector('.participating-doctor-select');
        const role = card.querySelector('.participating-doctor-role');
        const notes = card.querySelector('.participating-doctor-notes');
        
        if (select && select.value) {
            participating.push({
                doctor_id: parseInt(select.value),
                role: role ? role.value : 'طبيب مشارك',
                notes: notes ? notes.value : ''
            });
        }
    });
    
    return participating;
}
