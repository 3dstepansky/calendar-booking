import { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, ArrowRight, Check, Globe } from 'lucide-react';
import { bookingService } from './services/api';

// Компонент для обработки OAuth Callback
const AuthCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // React Router кладет параметры после /#/auth/callback? в location.search
    const params = new URLSearchParams(location.search);
    const token = params.get('token');
    if (token) {
      localStorage.setItem('token', token);
      navigate('/dashboard'); // Организатора отправляем сразу в настройки
    }
  }, [location, navigate]);

  return (
    <div className="text-center text-slate-400">
      Авторизация...
    </div>
  );
};

// Главный экран бронирования
const BookingScreen = () => {
  const [slots, setSlots] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [step, setStep] = useState(1);

  useEffect(() => {
    const fetchSlots = async () => {
      try {
        setLoading(true);
        // Берем слоты на сегодня для примера
        const today = new Date().toISOString().split('T')[0];
        const data = await bookingService.getAvailableSlots(today);
        setSlots(data);
      } catch (err) {
        console.error("Failed to fetch slots", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSlots();
  }, []);

  const handleBooking = async () => {
    if (!selectedSlot) return;
    try {
      const today = new Date().toISOString().split('T')[0];
      await bookingService.createBooking({
        start_time: `${today}T${selectedSlot}:00Z`,
        guest_name: "Telegram User", // В реальности берем из window.Telegram.WebApp.initDataUnsafe
        guest_email: "guest@example.com"
      });
      setStep(2);
    } catch (err) {
      alert("Ошибка при бронировании");
    }
  };

  return (
    <AnimatePresence mode="wait">
      {step === 1 ? (
        <motion.div key="selection" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <header>
            <div className="brand-badge">Live System</div>
            <h1>Записаться на встречу</h1>
            <div className="flex items-center gap-2 subtitle">
              <Globe size={14} /> 
              <span>UTC+3</span>
            </div>
          </header>

          {loading ? (
            <div className="py-20 text-center text-slate-500">Загрузка слотов...</div>
          ) : (
            <div className="slots-grid">
              {slots.length > 0 ? slots.map((slot) => (
                <button
                  key={slot}
                  onClick={() => setSelectedSlot(slot)}
                  className={`slot-button ${selectedSlot === slot ? 'active' : ''}`}
                >
                  <Clock size={14} />
                  {slot}
                </button>
              )) : (
                <div className="col-span-2 py-10 text-center text-slate-500">Нет свободных окон на сегодня</div>
              )}
            </div>
          )}

          <button
            disabled={!selectedSlot || loading}
            onClick={handleBooking}
            className="btn-continue"
          >
            Подтвердить запись
            <ArrowRight size={16} />
          </button>
        </motion.div>
      ) : (
        <motion.div key="success" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
              <Check className="text-black" size={32} />
            </div>
          </div>
          <h2 className="text-2xl font-medium mb-3">Готово!</h2>
          <p className="text-slate-400 mb-8 text-sm">
            Встреча подтверждена на <span className="text-white">{selectedSlot}</span>.
          </p>
          <button onClick={() => {setStep(1); setSelectedSlot(null);}} className="text-xs text-slate-500 hover:text-white underline underline-offset-4">
            Вернуться
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Экран авторизации организатора
const OrganizerLogin = () => {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4, ease: "easeOut" }} className="text-center">
      <header className="mb-8">
        <h1>Для Организаторов</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "15px", marginTop: "12px" }}>
          Войдите, чтобы настроить свое расписание и управлять встречами.
        </p>
      </header>
      
      <button 
        onClick={() => bookingService.login()}
        className="btn-primary btn-google"
      >
        <svg viewBox="0 0 24 24" width="22" height="22" xmlns="http://www.w3.org/2000/svg">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
        </svg>
        Продолжить с Google
      </button>
    </motion.div>
  );
};

// Экран панели управления (Настройки)
const OrganizerDashboard = () => {
  const [timezone, setTimezone] = useState("Europe/Moscow");
  const [saving, setSaving] = useState(false);

  // Для упрощения MVP берем жесткую настройку ПН-ПТ 09:00-18:00
  // В полноценной версии здесь должен быть список из 7 дней с input type="time"
  const defaultSchedule = [1, 2, 3, 4, 5].map(day => ({
    day_of_week: day,
    start_time: "09:00:00",
    end_time: "18:00:00"
  }));

  const handleSave = async () => {
    setSaving(true);
    try {
      await bookingService.updateProfile(timezone);
      await bookingService.updateWorkingHours(defaultSchedule);
      alert("Настройки успешно сохранены!");
    } catch (err) {
      alert("Ошибка сохранения. Убедитесь, что вы авторизованы.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="text-left w-full max-w-md mx-auto">
      <h1 style={{ marginBottom: "32px", textAlign: "center" }}>Настройки</h1>
      
      <div className="mb-6">
        <label>Ваш часовой пояс</label>
        <select 
          value={timezone} 
          onChange={(e) => setTimezone(e.target.value)}
        >
          <option value="Europe/Moscow">Москва (UTC+3)</option>
          <option value="Europe/London">Лондон (UTC+0)</option>
          <option value="Asia/Dubai">Дубай (UTC+4)</option>
        </select>
      </div>

      <div className="mb-8">
        <label>Рабочие часы (MVP)</label>
        <div className="schedule-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Пн — Пт</span>
            <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>09:00 - 18:00</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>В следующей версии появится возможность гибкой настройки каждого дня.</p>
        </div>
      </div>

      <button 
        onClick={handleSave} 
        disabled={saving}
        className="btn-primary"
      >
        {saving ? "Сохранение..." : "Сохранить изменения"}
      </button>
    </motion.div>
  );
};

function App() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6">
      <Router>
        <div className="booking-container">
          <Routes>
            <Route path="/" element={<BookingScreen />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/login" element={<OrganizerLogin />} />
            <Route path="/dashboard" element={<OrganizerDashboard />} />
          </Routes>
          <footer>
            <p>© 2026 Calendar Booking API</p>
          </footer>
        </div>
      </Router>
    </div>
  );
}

export default App;
