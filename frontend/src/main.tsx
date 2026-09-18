import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/app-shell";
import { HomePage } from "@/pages/home-page";
import { SeriesPage } from "@/pages/series-page";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/series/:seriesId" element={<SeriesPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
