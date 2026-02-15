// Search Module

const Search = {
    searchInput: null,
    searchResults: null,
    debounceTimer: null,

    init() {
        this.searchInput = document.getElementById('searchInput');
        this.searchResults = document.getElementById('searchResults');
        
        if (!this.searchInput || !this.searchResults) {
            return;
        }

        // Add event listener with debounce
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.performSearch(e.target.value);
            }, 300);
        });

        // Voice search button
        const voiceBtn = document.getElementById('voiceSearchBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                if (window.VoiceInput) {
                    window.VoiceInput.toggleListening(voiceBtn, 'searchInput');
                }
            });
        }
    },

    async performSearch(query) {
        if (!query || query.length < 2) {
            this.searchResults.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            this.displayResults(results);
        } catch (error) {
            console.error('Search error:', error);
            this.searchResults.innerHTML = '<p class="error">حدث خطأ في البحث</p>';
        }
    },

    displayResults(results) {
        if (results.length === 0) {
            this.searchResults.innerHTML = '<p class="no-data">لا توجد نتائج</p>';
            return;
        }

        const html = results.map(patient => `
            <div class="search-result-item" onclick="window.location.href='/patient/${patient.id}'">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <strong style="font-size: 1.1rem; color: #333;">${patient.name}</strong>
                        <div style="margin-top: 0.5rem; display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.9rem; color: #666;">
                            ${patient.phone ? `<span>📱 ${patient.phone}</span>` : ''}
                            ${patient.age ? `<span>🎂 ${patient.age} سنة</span>` : ''}
                            ${patient.blood_type ? `<span style="color: #dc3545; font-weight: bold;">🩸 ${patient.blood_type}</span>` : ''}
                        </div>
                        ${patient.national_id ? `<div style="margin-top: 0.3rem; font-size: 0.85rem; color: #999;">🆔 ${patient.national_id}</div>` : ''}
                    </div>
                    <div style="text-align: center; margin-right: 1rem;">
                        ${patient.total_debt > 0 ? 
                            `<div style="background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 8px; min-width: 80px;">
                                <div style="font-size: 0.75rem;">دين</div>
                                <div style="font-size: 1.2rem; font-weight: bold;">${patient.total_debt.toFixed(2)}</div>
                            </div>` :
                            `<span style="background: #28a745; color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: bold;">✅ مسدد</span>`
                        }
                    </div>
                </div>
            </div>
        `).join('');

        this.searchResults.innerHTML = html;
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Search.init());
} else {
    Search.init();
}
