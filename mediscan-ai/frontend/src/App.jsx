import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import XRayAnalysis from './pages/XRayAnalysis'
import Pipeline from './pages/Pipeline'
import Chat from './pages/Chat'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analysis" element={<XRayAnalysis />} />
          <Route path="/pipeline" element={<Pipeline />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
