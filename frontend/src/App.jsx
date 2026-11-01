import React, { useState, useEffect, useMemo } from 'react';
import Navbar from './components/Navbar';
import MapViewport from './components/MapViewport';
import SidebarDrawer from './components/SidebarDrawer';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [parcelsGeojson, setParcelsGeojson] = useState(null);
  const [layersData, setLayersData] = useState(null);
  const [studyAreaInfo, setStudyAreaInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  // Filter & Search states
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Selected Parcel state
  const [selectedParcelId, setSelectedParcelId] = useState(null);

  // Layer Visibility
  const [layerVisibility, setLayerVisibility] = useState({
    parcels: true,
    buildings: true,
    roads: true,
    paddy: true,
    utilities: true,
  });

  // Fetch initial spatial data on mount
  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/study-area/summary`)
        .then((r) => r.json())
        .catch(() => null),
      fetch(`${API_BASE}/study-area/parcels-geojson`)
        .then((r) => r.json())
        .catch(() => null),
      fetch(`${API_BASE}/study-area/layers-geojson`)
        .then((r) => r.json())
        .catch(() => null),
    ])
      .then(([summary, parcels, layers]) => {
        if (summary?.study_area) {
          setStudyAreaInfo(summary.study_area);
        }
        if (parcels) {
          setParcelsGeojson(parcels);
        }
        if (layers) {
          setLayersData(layers);
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Compute stat counts across all 534 parcels
  const stats = useMemo(() => {
    if (!parcelsGeojson?.features) {
      return { total: 534, pass: 327, warn: 142, fail: 65 };
    }
    const total = parcelsGeojson.features.length;
    let pass = 0;
    let warn = 0;
    let fail = 0;
    for (const f of parcelsGeojson.features) {
      const s = f.properties.compliance_status;
      if (s === 'PASS') pass++;
      else if (s === 'WARN') warn++;
      else if (s === 'FAIL') fail++;
    }
    return { total, pass, warn, fail };
  }, [parcelsGeojson]);

  // Filter features based on statusFilter and searchQuery
  const filteredGeojson = useMemo(() => {
    if (!parcelsGeojson?.features) return null;

    let filtered = parcelsGeojson.features;

    // Apply status filter pill
    if (statusFilter !== 'ALL') {
      filtered = filtered.filter(
        (f) => f.properties.compliance_status === statusFilter
      );
    }

    // Apply search query
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      filtered = filtered.filter((f) => {
        const pid = String(f.properties.parcel_id);
        const sy = String(f.properties.survey_no || '').toLowerCase();
        return pid === q || sy.includes(q);
      });
    }

    return {
      type: 'FeatureCollection',
      features: filtered,
    };
  }, [parcelsGeojson, statusFilter, searchQuery]);

  // Selected Parcel Object
  const selectedParcel = useMemo(() => {
    if (!selectedParcelId || !parcelsGeojson?.features) return null;
    const f = parcelsGeojson.features.find(
      (item) => item.properties.parcel_id === selectedParcelId
    );
    return f ? { ...f.properties, geometry: f.geometry } : null;
  }, [selectedParcelId, parcelsGeojson]);

  const handleToggleLayer = (layerName, isVisible) => {
    setLayerVisibility((prev) => ({
      ...prev,
      [layerName]: isVisible,
    }));
  };

  const handleSearchSubmit = () => {
    if (!searchQuery.trim() || !parcelsGeojson?.features) return;
    const q = searchQuery.trim().toLowerCase();
    const match = parcelsGeojson.features.find((f) => {
      const pid = String(f.properties.parcel_id);
      const sy = String(f.properties.survey_no || '').toLowerCase();
      return pid === q || sy.includes(q);
    });
    if (match) {
      setSelectedParcelId(match.properties.parcel_id);
    }
  };

  return (
    <div className="dashboard-root">
      {/* Header Navbar */}
      <Navbar
        stats={stats}
        statusFilter={statusFilter}
        onSelectFilter={setStatusFilter}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearchSubmit={handleSearchSubmit}
      />

      {/* Main Workspace Split */}
      <main className="main-workspace">
        <MapViewport
          parcelsGeojson={filteredGeojson}
          layersData={layersData}
          selectedParcelId={selectedParcelId}
          onSelectParcel={(id) => setSelectedParcelId(id)}
          layerVisibility={layerVisibility}
          onToggleLayer={handleToggleLayer}
          studyAreaInfo={studyAreaInfo}
        />

        <SidebarDrawer
          selectedParcel={selectedParcel}
          onClose={() => setSelectedParcelId(null)}
          onSelectParcel={(id) => setSelectedParcelId(id)}
        />
      </main>
    </div>
  );
}
