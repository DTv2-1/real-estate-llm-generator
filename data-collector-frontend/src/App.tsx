import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import DataCollector from './components/DataCollector';
import Chatbot from './components/Chatbot';
import PropertyList from './components/PropertyList';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/data-collector" element={<DataCollector />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/properties" element={<PropertyList />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
