import { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, ArrowRight, Check, Globe, Calendar, Settings, Trash2, ChevronRight, User } from 'lucide-react';
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

// Экран панели управления (Настройки + Список встреч)
const OrganizerDashboard = () => {
  const [activeTab, setActiveTab] = useState<'bookings' | 'settings'>('bookings');
  const [timezone, setTimezone] = useState("Europe/Moscow");
  const [bookings, setBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    setLoading(true);
    try {
      const data = await bookingService.getMyBookings();
      setBookings(data);
    } catch (err) {
      console.error("Failed to load bookings", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Вы уверены, что хотите отменить эту встречу? Она будет удалена из Google Календаря.")) return;
    try {
      await bookingService.deleteBooking(id);
      setBookings(bookings.filter(b => b.id !== id));
    } catch (err) {
      alert("Ошибка при отмене встречи.");
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      const defaultSchedule = [1, 2, 3, 4, 5].map(day => ({
        day_of_week: day,
        start_time: "09:00:00",
        end_time: "18:00:00"
      }));
      await bookingService.updateProfile(timezone);
      await bookingService.updateWorkingHours(defaultSchedule);
      alert("Настройки успешно сохранены!");
    } catch (err) {
      alert("Ошибка сохранения.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="w-full max-w-2xl mx-auto px-4 py-10">
      <div className="flex flex-col md:flex-row items-center justify-between mb-12 gap-6">
        <h1 className="!mb-0 text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/40 bg-clip-text text-transparent">
          Dashboard
        </h1>
        
        <div className="flex bg-white/[0.03] p-1.5 rounded-2xl border border-white/5 backdrop-blur-md">
          <button 
            onClick={() => setActiveTab('bookings')}
            className={`flex items-center gap-2.5 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${activeTab === 'bookings' ? 'bg-sky-500 text-white shadow-[0_0_20px_rgba(56,189,248,0.3)]' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Calendar size={18} /> Встречи
          </button>
          <button 
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2.5 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${activeTab === 'settings' ? 'bg-sky-500 text-white shadow-[0_0_20px_rgba(56,189,248,0.3)]' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Settings size={18} /> Настройки
          </button>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'bookings' ? (
          <motion.div key="bookings" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }}>
            {loading ? (
              <div className="flex flex-col items-center justify-center py-24 text-slate-500">
                <div className="w-10 h-10 border-2 border-sky-500/20 border-t-sky-500 rounded-full animate-spin mb-4" />
                <p className="text-sm tracking-wide">Синхронизация данных...</p>
              </div>
            ) : bookings.length === 0 ? (
              <div className="text-center py-24 bg-white/[0.02] rounded-[32px] border border-dashed border-white/10">
                <Calendar className="mx-auto text-slate-700 mb-5" size={48} />
                <p className="text-white text-lg font-medium">Пока пусто</p>
                <p className="text-slate-500 text-sm mt-2 max-w-xs mx-auto">Все ваши забронированные встречи из Google Календаря появятся здесь.</p>
              </div>
            ) : (
              <div className="grid gap-5">
                {bookings.map((b) => (
                  <motion.div 
                    layout
                    key={b.id} 
                    className="group relative bg-white/[0.03] hover:bg-white/[0.06] border border-white/5 p-6 rounded-3xl transition-all duration-300 flex justify-between items-center"
                  >
                    <div className="flex items-center gap-5">
                      <div className="h-14 w-14 rounded-2xl bg-sky-500/10 flex items-center justify-center text-sky-400 border border-sky-500/20 group-hover:scale-110 transition-transform duration-500">
                        <Clock size={24} />
                      </div>
                      <div>
                        <h4 className="text-xl font-semibold text-white tracking-tight">{b.guest_name}</h4>
                        <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-slate-400">
                          <span className="flex items-center gap-2 bg-white/5 px-2.5 py-1 rounded-lg border border-white/5">
                            <Clock size={14} className="text-sky-400" /> 
                            {new Date(b.start_time).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                          </span>
                          <span className="flex items-center gap-2 text-slate-500">
                            <User size={14} /> {b.guest_email}
                          </span>
                        </div>
                      </div>
                    </div>
                    <button 
                      onClick={() => handleDelete(b.id)}
                      className="p-3.5 rounded-2xl bg-red-500/0 text-slate-500 hover:bg-red-500/10 hover:text-red-400 transition-all duration-300"
                      title="Отменить встречу"
                    >
                      <Trash2 size={20} />
                    </button>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div key="settings" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }} className="bg-white/[0.03] p-10 rounded-[40px] border border-white/5 backdrop-blur-xl">
            <div className="mb-10">
              <label className="text-[11px] font-bold uppercase tracking-[0.2em] text-sky-500/70 mb-4 block">Ваш регион</label>
              <div className="relative group">
                <select 
                  value={timezone} 
                  onChange={(e) => setTimezone(e.target.value)}
                  className="w-full pl-6 pr-12 py-5 bg-black/40 border border-white/10 rounded-2xl focus:border-sky-500/50 transition-all duration-300 outline-none appearance-none cursor-pointer text-lg font-medium"
                >
                  <option value="Europe/Moscow">Москва (UTC+3)</option>
                  <option value="Europe/London">Лондон (UTC+0)</option>
                  <option value="Asia/Dubai">Дубай (UTC+4)</option>
                </select>
                <ChevronRight size={20} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-600 pointer-events-none group-hover:text-sky-500 transition-colors rotate-90" />
              </div>
            </div>
            
            <div className="mb-12">
              <label className="text-[11px] font-bold uppercase tracking-[0.2em] text-sky-500/70 mb-4 block">Рабочие часы</label>
              <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-1 h-full bg-sky-500/50" />
                <div className="flex justify-between items-center mb-4">
                  <span className="text-lg font-semibold text-white">Будни (Пн — Пт)</span>
                  <div className="bg-sky-500/10 text-sky-400 px-4 py-1.5 rounded-full text-sm font-bold border border-sky-500/20">
                    09:00 — 18:00
                  </div>
                </div>
                <p className="text-sm text-slate-500 leading-relaxed max-w-sm">
                  На данный момент настройки применяются ко всем будним дням автоматически. Индивидуальный выбор дней будет доступен в Step 4.
                </p>
              </div>
            </div>

            <button 
              onClick={handleSaveSettings} 
              disabled={saving} 
              className="btn-primary !py-5 !text-lg !rounded-2xl shadow-[0_10px_30px_-10px_rgba(56,189,248,0.5)] active:scale-[0.98]"
            >
              {saving ? (
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Сохранение...
                </div>
              ) : "Сохранить конфигурацию"}
            </button>
          </motion.div>
        )}
      </AnimatePresence>
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
