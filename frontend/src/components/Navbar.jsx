import React from 'react';
import { Layers, ShieldCheck, AlertTriangle, XCircle, Search, Compass } from 'lucide-react';

export default function Navbar({
  stats,
  statusFilter,
  onSelectFilter,
  searchQuery,
  onSearchChange,
  onSearchSubmit,
}) {
  return (
    <header className="navbar">
      {/* Brand Section */}
      <div className="brand-section">
        <div className="brand-logo">G+</div>
        <div>
          <h1 className="brand-title">GeoRAG+</h1>
        </div>
        <div className="jurisdiction-badge">
          <Compass size={14} />
          <span>Attingal Municipality (KMBR 2019)</span>
        </div>
      </div>

      {/* Filter / Stat Metric Chips */}
      <div className="stats-strip">
        <div
          id="filter-all"
          className={`stat-chip ${statusFilter === 'ALL' ? 'active' : ''}`}
          onClick={() => onSelectFilter('ALL')}
          title="Show all parcels in Attingal Study Ward"
        >
          <span className="dot all"></span>
          <span>All Plots:</span>
          <span className="val">{stats.total || 534}</span>
        </div>

        <div
          id="filter-pass"
          className={`stat-chip ${statusFilter === 'PASS' ? 'active' : ''}`}
          onClick={() => onSelectFilter('PASS')}
          title="Show compliant plots"
        >
          <span className="dot pass"></span>
          <span>Compliant:</span>
          <span className="val" style={{ color: '#10b981' }}>
            {stats.pass || 0}
          </span>
        </div>

        <div
          id="filter-warn"
          className={`stat-chip ${statusFilter === 'WARN' ? 'active' : ''}`}
          onClick={() => onSelectFilter('WARN')}
          title="Show plots needing legal/tax attention"
        >
          <span className="dot warn"></span>
          <span>Attention:</span>
          <span className="val" style={{ color: '#f59e0b' }}>
            {stats.warn || 0}
          </span>
        </div>

        <div
          id="filter-fail"
          className={`stat-chip ${statusFilter === 'FAIL' ? 'active' : ''}`}
          onClick={() => onSelectFilter('FAIL')}
          title="Show plots with statutory violations or restrictions"
        >
          <span className="dot fail"></span>
          <span>Violations:</span>
          <span className="val" style={{ color: '#f43f5e' }}>
            {stats.fail || 0}
          </span>
        </div>
      </div>

      {/* Search Input Box */}
      <form
        className="search-box"
        onSubmit={(e) => {
          e.preventDefault();
          onSearchSubmit();
        }}
      >
        <Search size={15} color="#94a3b8" />
        <input
          id="parcel-search-input"
          type="text"
          placeholder="Search Plot # or Survey (e.g. 1, 100/2)"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </form>
    </header>
  );
}
