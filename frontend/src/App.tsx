import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, ArrowRight, Check, Globe } from 'lucide-react';
import { bookingService } from './services/api';

// Компонент для обработки OAuth Callback
const AuthCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Google присылает токен в фрагменте #token=...
    const params = new URLSearchParams(location.hash.replace('#', '?'));
    const token = params.get('token');
    if (token) {
      localStorage.setItem('token', token);
      navigate('/');
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

function App() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6">
      <Router>
        <div className="booking-container">
          <Routes>
            <Route path="/" element={<BookingScreen />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
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
