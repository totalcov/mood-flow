// Конфигурация API
const API_BASE_URL = window.location.origin;
const MOODS_API_URL = `${API_BASE_URL}/moods/`;
const STATS_API_URL = `${API_BASE_URL}/moods/statistics/`;

// DOM элементы
const moodForm = document.getElementById('moodForm');
const moodList = document.getElementById('moodList');
const emptyState = document.getElementById('emptyState');
const loadingElement = document.getElementById('loading');
const messageElement = document.getElementById('message');
const refreshBtn = document.getElementById('refreshBtn');
const notesTextarea = document.getElementById('notes');
const charCount = document.getElementById('charCount');
const showStatsBtn = document.getElementById('showStatsBtn');
const closeStatsBtn = document.getElementById('closeStatsBtn');
const statsSection = document.getElementById('statsSection');
const loadStatsBtn = document.getElementById('loadStatsBtn');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const statsContent = document.getElementById('statsContent');
const filterDateInput = document.getElementById('filterDate');
const filterTypeInput = document.getElementById('filterType');
const applyFiltersBtn = document.getElementById('applyFilters');
const clearFiltersBtn = document.getElementById('clearFilters');

// Текущие фильтры
let currentFilters = {
    date_filter: null,
    mood_type: null
};

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

function initApp() {
    // Устанавливаем даты по умолчанию для статистики
    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 7);
    
    startDateInput.value = formatDate(weekAgo);
    endDateInput.value = formatDate(today);
    
    // Загружаем записи
    loadMoods();
    
    // Инициализируем выбор оценки
    initScoreSelector();
    
    // Инициализируем счетчик символов
    initCharCounter();
    
    // Устанавливаем обработчики событий
    setupEventListeners();
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Основные кнопки
    refreshBtn.addEventListener('click', () => loadMoods());
    showStatsBtn.addEventListener('click', () => toggleStatsSection(true));
    closeStatsBtn.addEventListener('click', () => toggleStatsSection(false));
    loadStatsBtn.addEventListener('click', loadStatistics);
    
    // Фильтры
    applyFiltersBtn.addEventListener('click', applyFilters);
    clearFiltersBtn.addEventListener('click', clearFilters);
    
    // Отправка формы
    moodForm.addEventListener('submit', handleFormSubmit);
}

// Инициализация выбора оценки
function initScoreSelector() {
    const scoreButtons = document.querySelectorAll('.score-btn');
    const hiddenInput = document.getElementById('mood_score');
    
    scoreButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Удаляем active у всех кнопок
            scoreButtons.forEach(b => b.classList.remove('active'));
            
            // Добавляем active к текущей кнопке
            this.classList.add('active');
            
            // Обновляем скрытое поле
            hiddenInput.value = this.dataset.value;
        });
    });
}

// Инициализация счетчика символов
function initCharCounter() {
    notesTextarea.addEventListener('input', function() {
        const length = this.value.length;
        charCount.textContent = length;
        
        if (length > 450) {
            charCount.style.color = '#e53e3e';
        } else if (length > 400) {
            charCount.style.color = '#ed8936';
        } else {
            charCount.style.color = '#888';
        }
    });
}

// Загрузка всех записей о настроениях
async function loadMoods(filters = currentFilters) {
    showLoading(true);
    hideMessage();
    
    try {
        // Строим URL с параметрами
        const url = new URL(MOODS_API_URL);
        if (filters.date_filter) {
            url.searchParams.append('date_filter', filters.date_filter);
        }
        if (filters.mood_type) {
            url.searchParams.append('mood_type', filters.mood_type);
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        const moods = await response.json();
        
        showLoading(false);
        
        if (moods.length === 0) {
            showEmptyState(true);
            return;
        }
        
        showEmptyState(false);
        renderMoods(moods);
        
    } catch (error) {
        console.error('Ошибка при загрузке настроений:', error);
        showLoading(false);
        showMessage('Не удалось загрузить записи. Попробуйте обновить страницу.', 'error');
    }
}

// Отображение списка настроений
function renderMoods(moods) {
    // Сортируем по дате (сначала новые)
    moods.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    moodList.innerHTML = '';
    
    moods.forEach(mood => {
        const moodCard = createMoodCard(mood);
        moodList.appendChild(moodCard);
    });
}

// Создание карточки настроения
function createMoodCard(mood) {
    const card = document.createElement('div');
    card.className = 'mood-card';
    card.setAttribute('data-score', mood.mood_score);
    
    // Преобразуем дату в читаемый формат
    const date = new Date(mood.created_at);
    const formattedDate = date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const simpleDate = mood.date ? new Date(mood.date).toLocaleDateString('ru-RU') : 'Нет даты';
    
    card.innerHTML = `
        <div class="mood-header">
            <div class="mood-type">
                <i class="fas fa-smile"></i> ${mood.mood_type}
            </div>
            <div class="mood-score">
                Оценка: <strong>${mood.mood_score}/5</strong>
            </div>
        </div>
        
        <div class="mood-date">
            <i class="far fa-calendar"></i> ${simpleDate} 
            <i class="far fa-clock" style="margin-left: 15px;"></i> ${formattedDate}
        </div>
        
        ${mood.notes ? `
            <div class="mood-notes">
                <i class="fas fa-quote-left"></i> ${mood.notes}
            </div>
        ` : ''}
    `;
    
    return card;
}

// Обработка отправки формы
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        mood_type: document.getElementById('mood_type').value.trim(),
        mood_score: parseInt(document.getElementById('mood_score').value),
        notes: document.getElementById('notes').value.trim() || null
    };
    
    // Валидация
    if (!formData.mood_type) {
        showMessage('Пожалуйста, введите тип настроения', 'error');
        return;
    }
    
    if (formData.mood_type.length > 50) {
        showMessage('Тип настроения не должен превышать 50 символов', 'error');
        return;
    }
    
    if (formData.mood_score < 1 || formData.mood_score > 5) {
        showMessage('Оценка должна быть от 1 до 5', 'error');
        return;
    }
    
    try {
        showMessage('Сохранение настроения...', 'info');
        
        const response = await fetch(MOODS_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Ошибка HTTP: ${response.status}`);
        }
        
        const newMood = await response.json();
        
        // Показываем сообщение об успехе
        showMessage('Настроение успешно сохранено!', 'success');
        
        // Сбрасываем форму
        moodForm.reset();
        document.getElementById('mood_score').value = '3';
        document.querySelectorAll('.score-btn').forEach((btn, index) => {
            btn.classList.toggle('active', index === 2); // 3 по умолчанию
        });
        charCount.textContent = '0';
        
        // Загружаем обновленный список
        setTimeout(() => {
            hideMessage();
            loadMoods();
        }, 1500);
        
    } catch (error) {
        console.error('Ошибка при сохранении настроения:', error);
        showMessage(`Ошибка: ${error.message}`, 'error');
    }
}

// Управление секцией статистики
function toggleStatsSection(show) {
    statsSection.style.display = show ? 'block' : 'none';
    showStatsBtn.style.display = show ? 'none' : 'flex';
}

// Загрузка статистики
async function loadStatistics() {
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    if (!startDate || !endDate) {
        showMessage('Пожалуйста, выберите начальную и конечную дату', 'error');
        return;
    }
    
    try {
        showMessage('Загрузка статистики...', 'info');
        
        const url = new URL(STATS_API_URL);
        url.searchParams.append('start_date', startDate);
        url.searchParams.append('end_date', endDate);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}`);
        }
        
        const stats = await response.json();
        renderStatistics(stats);
        hideMessage();
        
    } catch (error) {
        console.error('Ошибка при загрузке статистики:', error);
        showMessage(`Ошибка: ${error.message}`, 'error');
    }
}

// Отображение статистики
function renderStatistics(stats) {
    statsContent.innerHTML = `
        <div class="stat-item">
            <div class="stat-label">Средняя оценка настроения:</div>
            <div class="stat-value">${stats.average_score || 0}</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Всего записей за период:</div>
            <div class="stat-value">${stats.total_entries || 0}</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Распределение по типам:</div>
            ${stats.mood_types && Object.keys(stats.mood_types).length > 0 ? `
                <div class="mood-types-list">
                    ${Object.entries(stats.mood_types).map(([type, count]) => `
                        <div class="mood-type-badge">
                            ${type}: ${count}
                        </div>
                    `).join('')}
                </div>
            ` : '<div class="stat-value">Нет данных</div>'}
        </div>
    `;
}

// Применение фильтров
function applyFilters() {
    currentFilters = {
        date_filter: filterDateInput.value || null,
        mood_type: filterTypeInput.value.trim() || null
    };
    
    loadMoods(currentFilters);
    
    if (currentFilters.date_filter || currentFilters.mood_type) {
        showMessage('Фильтры применены', 'info');
        setTimeout(hideMessage, 2000);
    }
}

// Сброс фильтров
function clearFilters() {
    filterDateInput.value = '';
    filterTypeInput.value = '';
    currentFilters = {
        date_filter: null,
        mood_type: null
    };
    
    loadMoods();
    showMessage('Фильтры сброшены', 'info');
    setTimeout(hideMessage, 2000);
}

// Вспомогательные функции
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function showLoading(show) {
    loadingElement.style.display = show ? 'block' : 'none';
}

function showEmptyState(show) {
    emptyState.style.display = show ? 'block' : 'none';
    moodList.style.display = show ? 'none' : 'grid';
}

function showMessage(text, type = 'info') {
    messageElement.textContent = text;
    messageElement.className = `message ${type}`;
    messageElement.style.display = 'block';
}

function hideMessage() {
    messageElement.style.display = 'none';
}

// Экспортируем функции для отладки (опционально)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadMoods,
        createMoodCard,
        handleFormSubmit,
        loadStatistics
    };
}




// Отображение статистики
function renderStatistics(stats) {
    // Создаем распределение по оценкам
    const scoreDistribution = {};
    if (stats.entries_data) {
        stats.entries_data.forEach(entry => {
            const score = entry.mood_score;
            scoreDistribution[score] = (scoreDistribution[score] || 0) + 1;
        });
    }
    
    // Создаем HTML для распределения по оценкам
    let scoreDistributionHTML = '';
    if (Object.keys(scoreDistribution).length > 0) {
        scoreDistributionHTML = `
            <div class="distribution-chart">
                ${Object.entries(scoreDistribution).sort((a, b) => a[0] - b[0]).map(([score, count]) => {
                    const percentage = ((count / stats.total_entries) * 100).toFixed(1);
                    return `
                        <div class="distribution-item">
                            <div class="distribution-header">
                                <span class="score-label">Оценка ${score}</span>
                                <span class="score-count">${count} зап.</span>
                            </div>
                            <div class="distribution-bar">
                                <div class="distribution-fill" style="width: ${percentage}%" 
                                     data-score="${score}"></div>
                            </div>
                            <div class="distribution-percentage">${percentage}%</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    } else {
        scoreDistributionHTML = '<div class="stat-value">Нет данных по оценкам</div>';
    }
    
    statsContent.innerHTML = `
        <div class="stat-item">
            <div class="stat-label">Средняя оценка настроения:</div>
            <div class="stat-value large">${stats.average_score || 0}</div>
            <div class="stat-hint">по шкале от 1 до 5</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Всего записей за период:</div>
            <div class="stat-value">${stats.total_entries || 0}</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Распределение по оценкам:</div>
            ${scoreDistributionHTML}
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Распределение по типам:</div>
            ${stats.mood_types && Object.keys(stats.mood_types).length > 0 ? `
                <div class="mood-types-list">
                    ${Object.entries(stats.mood_types).map(([type, count]) => `
                        <div class="mood-type-badge" title="${type}">
                            <span class="type-icon">${getMoodIcon(type)}</span>
                            <span class="type-name">${type.length > 15 ? type.substring(0, 15) + '...' : type}</span>
                            <span class="type-count">${count}</span>
                        </div>
                    `).join('')}
                </div>
            ` : '<div class="stat-value">Нет данных</div>'}
        </div>
    `;
}

// Функция для определения иконки по типу настроения
function getMoodIcon(moodType) {
    const type = moodType.toLowerCase();
    
    if (type.includes('счастлив') || type.includes('радост') || type.includes('happy') || type.includes('excited')) {
        return '😊';
    } else if (type.includes('грустн') || type.includes('печаль') || type.includes('sad') || type.includes('depressed')) {
        return '😔';
    } else if (type.includes('зл') || type.includes('angry') || type.includes('mad') || type.includes('annoyed')) {
        return '😠';
    } else if (type.includes('спокойн') || type.includes('calm') || type.includes('peaceful') || type.includes('relaxed')) {
        return '😌';
    } else if (type.includes('устал') || type.includes('tired') || type.includes('exhausted')) {
        return '😴';
    } else if (type.includes('взволнован') || type.includes('excited') || type.includes('energetic')) {
        return '😃';
    } else if (type.includes('тревож') || type.includes('anxious') || type.includes('worried')) {
        return '😰';
    } else if (type.includes('нейтраль') || type.includes('neutral') || type.includes('normal')) {
        return '😐';
    } else if (type.includes('любов') || type.includes('love') || type.includes('loving')) {
        return '😍';
    } else if (type.includes('удивл') || type.includes('surprised') || type.includes('shocked')) {
        return '😲';
    }
    
    // Дефолтные иконки по оценке (если тип не распознан)
    return '😐';
}

// Обновляем функцию getMoodIcon для карточек (добавляем в существующую)
function getMoodIconByTypeAndScore(moodType, score) {
    const type = moodType.toLowerCase();
    
    // Сначала пытаемся определить по типу
    if (type.includes('счастлив') || type.includes('радост') || type.includes('happy') || type.includes('excited')) {
        return '😊';
    } else if (type.includes('грустн') || type.includes('печаль') || type.includes('sad') || type.includes('depressed')) {
        return '😔';
    } else if (type.includes('зл') || type.includes('angry') || type.includes('mad') || type.includes('annoyed')) {
        return '😠';
    } else if (type.includes('спокойн') || type.includes('calm') || type.includes('peaceful') || type.includes('relaxed')) {
        return '😌';
    } else if (type.includes('устал') || type.includes('tired') || type.includes('exhausted')) {
        return '😴';
    } else if (type.includes('взволнован') || type.includes('excited') || type.includes('energetic')) {
        return '😃';
    } else if (type.includes('тревож') || type.includes('anxious') || type.includes('worried')) {
        return '😰';
    } else if (type.includes('нейтраль') || type.includes('neutral') || type.includes('normal')) {
        return '😐';
    }
    
    // Если тип не распознан, используем оценку
    switch(parseInt(score)) {
        case 1: return '😢';
        case 2: return '😔';
        case 3: return '😐';
        case 4: return '🙂';
        case 5: return '😊';
        default: return '😐';
    }
}

// Обновляем функцию createMoodCard:
function createMoodCard(mood) {
    const card = document.createElement('div');
    card.className = 'mood-card';
    card.setAttribute('data-score', mood.mood_score);
    
    // Преобразуем дату в читаемый формат
    const date = new Date(mood.created_at);
    const formattedDate = date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const simpleDate = mood.date ? new Date(mood.date).toLocaleDateString('ru-RU') : 'Нет даты';
    
    // Получаем правильную иконку
    const moodIcon = getMoodIconByTypeAndScore(mood.mood_type, mood.mood_score);
    
    card.innerHTML = `
        <div class="mood-header">
            <div class="mood-type">
                <span class="mood-icon">${moodIcon}</span> ${mood.mood_type}
            </div>
            <div class="mood-score">
                Оценка: <strong>${mood.mood_score}/5</strong>
            </div>
        </div>
        
        <div class="mood-date">
            <i class="far fa-calendar"></i> ${simpleDate} 
            <i class="far fa-clock" style="margin-left: 15px;"></i> ${formattedDate}
        </div>
        
        ${mood.notes ? `
            <div class="mood-notes">
                <i class="fas fa-quote-left"></i> ${mood.notes}
            </div>
        ` : ''}
    `;
    
    return card;
}