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

// ДОСКА НАСТРОЕНИЙ - DOM элементы
const moodBoardSection = document.getElementById('moodBoardSection');
const currentMonthElement = document.getElementById('currentMonth');
const prevMonthBtn = document.getElementById('prevMonthBtn');
const nextMonthBtn = document.getElementById('nextMonthBtn');
const moodCalendar = document.getElementById('moodCalendar');
const calendarLoading = document.getElementById('calendarLoading');
const dayTooltip = document.getElementById('dayTooltip');

// Текущие фильтры
let currentFilters = {
    date_filter: null,
    mood_type: null
};

// Текущий месяц и год для доски
let currentBoardDate = {
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1
};

// Объект для перевода типов настроения на русский
const moodTypeLabels = {
    'happy': 'Радостное',
    'sad': 'Грустное',
    'energetic': 'Энергичное',
    'calm': 'Спокойное',
    'anxious': 'Тревожное',
    'neutral': 'Нейтральное'
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
    
    // Инициализируем выбор оценки
    initScoreSelector();
    
    // Инициализируем счетчик символов
    initCharCounter();
    
    // Загружаем записи
    loadMoods();
    
    // Инициализируем доску настроений
    initMoodBoard();
    
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
    
    // Получаем иконку
    const moodIcon = getMoodIcon(mood.mood_score);
    
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

// Функция для получения иконки по оценке
function getMoodIcon(score) {
    switch(parseInt(score)) {
        case 1: return '😢';
        case 2: return '😔';
        case 3: return '😐';
        case 4: return '🙂';
        case 5: return '😊';
        default: return '😐';
    }
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
        
        // Загружаем обновленный список и календарь
        setTimeout(() => {
            hideMessage();
            loadMoods();
            loadMoodCalendar(); // Обновляем календарь
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
                            <span class="type-name">${type.length > 15 ? type.substring(0, 15) + '...' : type}</span>
                            <span class="type-count">${count}</span>
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

// ===========================================
// ДОСКА НАСТРОЕНИЙ - КОМПАКТНАЯ ВЕРСИЯ
// ===========================================

// Инициализация доски
function initMoodBoard() {
    console.log('Инициализация доски настроений...');
    loadMoodCalendar();
    setupBoardEventListeners();
}

// Настройка обработчиков для доски
function setupBoardEventListeners() {
    prevMonthBtn.addEventListener('click', () => changeMonth(-1));
    nextMonthBtn.addEventListener('click', () => changeMonth(1));
    
    // Закрытие тултипа при клике вне
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.day-cell-compact')) {
            hideDayTooltip();
        }
    });
}

// Загрузка календаря
async function loadMoodCalendar() {
    showCalendarLoading(true);
    console.log('Загрузка календаря за', currentBoardDate.year, currentBoardDate.month);
    
    try {
        const url = new URL(`${API_BASE_URL}/moods/calendar/`);
        url.searchParams.append('year', currentBoardDate.year);
        url.searchParams.append('month', currentBoardDate.month);
        
        console.log('Запрос к:', url.toString());
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Ошибка HTTP: ${response.status}. Проверьте бэкенд.`);
        }
        
        const calendarData = await response.json();
        console.log('Данные календаря получены:', calendarData);
        
        renderMoodCalendar(calendarData);
        
    } catch (error) {
        console.error('Ошибка при загрузке календаря:', error);
        
        // Показываем сообщение об ошибке
        moodCalendar.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 20px; color: #e53e3e;">
                <i class="fas fa-exclamation-triangle"></i><br>
                Ошибка загрузки календаря<br>
                <small style="color: #a0aec0;">${error.message}</small>
            </div>
        `;
        
        showCalendarLoading(false);
    }
}

// Отображение компактного календаря
function renderMoodCalendar(calendarData) {
    // Обновляем заголовок
    currentMonthElement.textContent = `${calendarData.month_name} ${calendarData.year}`;
    
    // Очищаем календарь
    moodCalendar.innerHTML = '';
    
    // Дни недели
    const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    dayNames.forEach(dayName => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'day-cell-compact empty';
        dayHeader.textContent = dayName;
        dayHeader.style.color = '#718096';
        dayHeader.style.fontWeight = '600';
        dayHeader.style.cursor = 'default';
        moodCalendar.appendChild(dayHeader);
    });
    
    // Определяем день недели первого дня месяца
    const firstDay = new Date(calendarData.year, calendarData.month - 1, 1);
    let firstDayOfWeek = firstDay.getDay(); // 0=Вс, 1=Пн, ..., 6=Сб
    
    // Преобразуем к нашему формату (0=Пн, 6=Вс)
    firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;
    
    // Добавляем пустые ячейки для выравнивания
    for (let i = 0; i < firstDayOfWeek; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'day-cell-compact empty';
        emptyCell.style.visibility = 'hidden';
        moodCalendar.appendChild(emptyCell);
    }
    
    // Добавляем ячейки для каждого дня месяца
    const daysInMonth = calendarData.total_days;
    const today = new Date();
    
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${calendarData.year}-${String(calendarData.month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayData = calendarData.calendar[dateStr] || {
            score: 0,
            mood_type: null,
            color: '#e2e8f0',
            has_data: false,
            notes: ''
        };
        
        const dayCell = createCompactDayCell(day, dayData, dateStr, today);
        moodCalendar.appendChild(dayCell);
    }
    
    showCalendarLoading(false);
}

// Создание компактной ячейки дня
function createCompactDayCell(dayNumber, dayData, dateStr, today) {
    const dayCell = document.createElement('div');
    dayCell.className = 'day-cell-compact';
    dayCell.style.backgroundColor = dayData.color;
    dayCell.textContent = dayNumber;
    dayCell.dataset.date = dateStr;
    dayCell.dataset.score = dayData.score;
    dayCell.dataset.mood = dayData.mood_type || '';
    dayCell.dataset.notes = dayData.notes || '';
    
    // Выделяем сегодняшний день
    const cellDate = new Date(dateStr);
    const isToday = cellDate.getDate() === today.getDate() && 
                   cellDate.getMonth() === today.getMonth() && 
                   cellDate.getFullYear() === today.getFullYear();
    
    if (isToday) {
        dayCell.classList.add('today');
    }
    
    // Индикатор данных (точка в углу)
    if (dayData.has_data) {
        const dot = document.createElement('div');
        dot.className = 'has-data-dot';
        dayCell.appendChild(dot);
    }
    
    // Тултип при наведении
    dayCell.addEventListener('mouseenter', (e) => {
        showDayTooltip(e, dayNumber, dayData, dateStr);
    });
    
    dayCell.addEventListener('mouseleave', () => {
        hideDayTooltip();
    });
    
    // Клик для фильтрации
    dayCell.addEventListener('click', () => {
        if (dayData.has_data) {
            filterByDate(dateStr);
        } else {
            // Если нет данных, предлагаем добавить
            showMessage(`Выбрана дата: ${formatDisplayDate(dateStr)}. Заполните форму.`, 'info');
        }
    });
    
    return dayCell;
}

// Функция для форматирования даты
function formatDisplayDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long'
    });
}

// Показать тултип
function showDayTooltip(event, dayNumber, dayData, dateStr) {
    const date = new Date(dateStr);
    const formattedDate = date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    let tooltipHTML = `<div class="tooltip-date">${formattedDate}</div>`;
    
    if (dayData.has_data) {
        tooltipHTML += `
            <div><strong>${dayData.mood_type || 'Не указано'}</strong></div>
            <div>Оценка: <strong>${dayData.score}/5</strong></div>
        `;
        
        if (dayData.notes) {
            const shortNotes = dayData.notes.length > 60 
                ? dayData.notes.substring(0, 60) + '...' 
                : dayData.notes;
            tooltipHTML += `<div class="tooltip-mood">"${shortNotes}"</div>`;
        }
    } else {
        tooltipHTML += '<div><em>Нет записи о настроении</em></div>';
    }
    
    dayTooltip.innerHTML = tooltipHTML;
    dayTooltip.style.display = 'block';
    
    // Позиционируем тултип
    const rect = event.target.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    dayTooltip.style.left = `${rect.left + window.scrollX}px`;
    dayTooltip.style.top = `${rect.top + scrollTop - dayTooltip.offsetHeight - 10}px`;
    
    // Плавное появление
    setTimeout(() => {
        dayTooltip.style.opacity = '1';
        dayTooltip.style.transform = 'translateY(0)';
    }, 10);
}

// Скрыть тултип
function hideDayTooltip() {
    dayTooltip.style.opacity = '0';
    dayTooltip.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
        dayTooltip.style.display = 'none';
    }, 200);
}

// Изменение месяца
function changeMonth(delta) {
    let newMonth = currentBoardDate.month + delta;
    let newYear = currentBoardDate.year;
    
    if (newMonth > 12) {
        newMonth = 1;
        newYear++;
    } else if (newMonth < 1) {
        newMonth = 12;
        newYear--;
    }
    
    currentBoardDate.month = newMonth;
    currentBoardDate.year = newYear;
    
    loadMoodCalendar();
}

// Показать/скрыть загрузку календаря
function showCalendarLoading(show) {
    if (calendarLoading) {
        calendarLoading.style.display = show ? 'flex' : 'none';
    }
    if (moodCalendar) {
        moodCalendar.style.opacity = show ? '0.5' : '1';
    }
}

// Фильтрация по дате
function filterByDate(dateStr) {
    filterDateInput.value = dateStr;
    applyFilters();
    
    // Прокручиваем к списку
    setTimeout(() => {
        document.querySelector('.mood-list-section').scrollIntoView({
            behavior: 'smooth'
        });
    }, 300);
}

// ===========================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ===========================================

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function showLoading(show) {
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

function showEmptyState(show) {
    if (emptyState && moodList) {
        emptyState.style.display = show ? 'block' : 'none';
        moodList.style.display = show ? 'none' : 'grid';
    }
}

function showMessage(text, type = 'info') {
    if (messageElement) {
        messageElement.textContent = text;
        messageElement.className = `message ${type}`;
        messageElement.style.display = 'block';
    }
}

function hideMessage() {
    if (messageElement) {
        messageElement.style.display = 'none';
    }
}

// Тестовая функция для проверки
function testAllAPIs() {
    console.log('=== ТЕСТИРОВАНИЕ API ===');
    console.log('API Base URL:', API_BASE_URL);
    console.log('Moods API URL:', MOODS_API_URL);
    console.log('Calendar API URL:', `${API_BASE_URL}/moods/calendar/`);
    
    // Тест календаря
    fetch(`${API_BASE_URL}/moods/calendar/`)
        .then(response => {
            console.log('Calendar API Status:', response.status);
            return response.json();
        })
        .then(data => console.log('Calendar API Response:', data))
        .catch(error => console.error('Calendar API Error:', error));
}

// Запускаем тест при загрузке
window.addEventListener('load', () => {
    console.log('=== MOOD FLOW ЗАГРУЖЕН ===');
    testAllAPIs();
});