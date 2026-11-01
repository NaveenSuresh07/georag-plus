import React, { useState, useEffect } from 'react';
import {
  X,
  FileCheck2,
  Building2,
  BadgeDollarSign,
  Bot,
  AlertCircle,
  CheckCircle2,
  Clock,
  Sparkles,
  Calculator,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function SidebarDrawer({
  selectedParcel,
  onClose,
  onSelectParcel,
}) {
  const [activeTab, setActiveTab] = useState('phase1');

  // Phase data states
  const [p1Data, setP1Data] = useState(null);
  const [p2Data, setP2Data] = useState(null);
  const [p3Data, setP3Data] = useState(null);
  const [loading, setLoading] = useState(false);

  // Phase 1 interactive inputs
  const [declaredPrice, setDeclaredPrice] = useState(3000000);

  // Phase 2 interactive inputs
  const [p2Floors, setP2Floors] = useState(2);
  const [p2Height, setP2Height] = useState(7.0);
  const [p2CostSqm, setP2CostSqm] = useState(30000);

  // Phase 3 interactive inputs
  const [salePrice, setSalePrice] = useState(5000000);
  const [acqCost, setAcqCost] = useState(2500000);
  const [acqDate, setAcqDate] = useState('2021-06-15');

  // AI Agent states
  const [aiQuery, setAiQuery] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);

  const parcelId = selectedParcel?.parcel_id;

  // Fetch phase data when parcelId changes
  useEffect(() => {
    if (!parcelId) return;

    setLoading(true);
    setAiResponse(null);

    // Set sensible default prices based on fair value
    const fv = selectedParcel.fair_value_total || 3000000;
    const initialSale = Math.max(fv, 4500000);
    setDeclaredPrice(initialSale);
    setSalePrice(initialSale);

    Promise.all([
      fetch(`${API_BASE}/phase1/${parcelId}?consideration=${initialSale}&ec_years=30`)
        .then((r) => r.json())
        .catch(() => null),
      fetch(`${API_BASE}/phase2/${parcelId}?floors=2&height_m=7.0&cost_per_sqm=30000`)
        .then((r) => r.json())
        .catch(() => null),
      fetch(
        `${API_BASE}/phase3/${parcelId}?sale_price=${initialSale}&acquisition_cost=2500000&acquisition_date=2021-06-15`
      )
        .then((r) => r.json())
        .catch(() => null),
    ])
      .then(([d1, d2, d3]) => {
        setP1Data(d1);
        setP2Data(d2);
        setP3Data(d3);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [parcelId]);

  // Recalculate Phase 1
  const recalculatePhase1 = () => {
    if (!parcelId) return;
    fetch(`${API_BASE}/phase1/${parcelId}?consideration=${declaredPrice}&ec_years=30`)
      .then((r) => r.json())
      .then((d) => setP1Data(d))
      .catch(() => null);
  };

  // Recalculate Phase 2
  const recalculatePhase2 = () => {
    if (!parcelId) return;
    fetch(
      `${API_BASE}/phase2/${parcelId}?floors=${p2Floors}&height_m=${p2Height}&cost_per_sqm=${p2CostSqm}`
    )
      .then((r) => r.json())
      .then((d) => setP2Data(d))
      .catch(() => null);
  };

  // Recalculate Phase 3
  const recalculatePhase3 = () => {
    if (!parcelId) return;
    fetch(
      `${API_BASE}/phase3/${parcelId}?sale_price=${salePrice}&acquisition_cost=${acqCost}&acquisition_date=${acqDate}`
    )
      .then((r) => r.json())
      .then((d) => setP3Data(d))
      .catch(() => null);
  };

  // Run AI Explainer Query
  const runAiQuery = (customQuery) => {
    const q = customQuery || aiQuery;
    if (!q || !parcelId) return;

    setAiLoading(true);
    fetch(`${API_BASE}/agent/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: q,
        parcel_id: parcelId,
        floors: p2Floors,
        height_m: p2Height,
        sale_price: salePrice,
        acquisition_cost: acqCost,
        acquisition_date: acqDate,
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        setAiResponse(data);
        setAiLoading(false);
      })
      .catch(() => setAiLoading(false));
  };

  // Empty state when no plot is clicked
  if (!selectedParcel) {
    return (
      <aside className="sidebar-drawer">
        <div className="sidebar-empty-state">
          <div className="empty-icon">
            <Building2 size={32} />
          </div>
          <h2 className="empty-title">Select a Plot on the Map</h2>
          <p style={{ fontSize: '0.85rem', lineHeight: '1.5' }}>
            Click any cadastral parcel in the Attingal Study Ward to audit
            Phase 1 (Buying Title), Phase 2 (KMBR Building Rules), and Phase 3
            (Selling Compliance & Taxes).
          </p>

          <div className="demo-plots-grid">
            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(1)}
              id="demo-plot-1"
            >
              <div className="demo-plot-title">Plot #1 (Standard)</div>
              <div className="demo-plot-desc">Side Setback Violation, Valid OC</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(2)}
              id="demo-plot-2"
            >
              <div className="demo-plot-title" style={{ color: '#f43f5e' }}>
                Plot #2 (Unauthorized)
              </div>
              <div className="demo-plot-desc">UA Door No, Double Tax, No OC</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(3)}
              id="demo-plot-3"
            >
              <div className="demo-plot-title" style={{ color: '#f59e0b' }}>
                Plot #3 (Pending OC)
              </div>
              <div className="demo-plot-desc">Rule 20 Inspection Pending</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(4)}
              id="demo-plot-4"
            >
              <div className="demo-plot-title" style={{ color: '#f59e0b' }}>
                Plot #4 (Tax Arrears)
              </div>
              <div className="demo-plot-desc">Rs 14,500 Municipal Dues</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(5)}
              id="demo-plot-5"
            >
              <div className="demo-plot-title">Plot #5 (Bare Land)</div>
              <div className="demo-plot-desc">Vacant Plot, High Fair Value TDS</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(10)}
              id="demo-plot-10"
            >
              <div className="demo-plot-title" style={{ color: '#f43f5e' }}>
                Plot #10 (Paddy Act)
              </div>
              <div className="demo-plot-desc">Paddy Data Bank Conflict</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(42)}
              id="demo-plot-42"
            >
              <div className="demo-plot-title" style={{ color: '#f43f5e' }}>
                Plot #42 (Steep Slope)
              </div>
              <div className="demo-plot-desc">24.5% Slope &gt; 20% Limit</div>
            </div>

            <div
              className="demo-plot-card"
              onClick={() => onSelectParcel(43)}
              id="demo-plot-43"
            >
              <div className="demo-plot-title" style={{ color: '#f59e0b' }}>
                Plot #43 (Retaining Wall)
              </div>
              <div className="demo-plot-desc">22.8% Slope With Retaining Wall</div>
            </div>
          </div>
        </div>
      </aside>
    );
  }

  const props = selectedParcel;
  const status = props.compliance_status || 'PASS';

  return (
    <aside className="sidebar-drawer">
      {/* Header Info Card */}
      <div className="parcel-header-card">
        <div className="parcel-header-top">
          <div>
            <div className="parcel-id-tag">Plot #{props.parcel_id}</div>
            <div className="parcel-meta-sub">
              <span>Sy No: <b>{props.survey_no}</b></span>
              <span>•</span>
              <span>TP: <b>{props.thandaper_no}</b></span>
              <span>•</span>
              <span>{props.village}</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className={`status-pill ${status.toLowerCase()}`}>
              [{status}]
            </span>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
              }}
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Key Dimensions Strip */}
        <div className="metrics-keyval-grid">
          <div className="kv-cell">
            <div className="kv-label">Plot Area</div>
            <div className="kv-value">
              {props.area_sqm} m²{' '}
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                ({(props.area_sqm * 0.0247105).toFixed(2)} Cents)
              </span>
            </div>
          </div>
          <div className="kv-cell">
            <div className="kv-label">Land Classification</div>
            <div className="kv-value">{props.land_type}</div>
          </div>
          <div className="kv-cell">
            <div className="kv-label">Fair Value / Are</div>
            <div className="kv-value">
              ₹{(props.fair_value_per_are || 0).toLocaleString('en-IN')}
            </div>
          </div>
          <div className="kv-cell">
            <div className="kv-label">Door Number</div>
            <div className="kv-value">{props.door_no || 'Unassigned'}</div>
          </div>
        </div>

        {/* Flag Reasons */}
        {props.reasons && props.reasons.length > 0 && status !== 'PASS' && (
          <div className="reasons-banner">
            {props.reasons.map((r, i) => (
              <div key={i} style={{ display: 'flex', gap: '6px' }}>
                <span>•</span>
                <span>{r}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tabs Navigation */}
      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'phase1' ? 'active' : ''}`}
          onClick={() => setActiveTab('phase1')}
        >
          <FileCheck2 size={15} />
          <span>1. Buying</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'phase2' ? 'active' : ''}`}
          onClick={() => setActiveTab('phase2')}
        >
          <Building2 size={15} />
          <span>2. Building</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'phase3' ? 'active' : ''}`}
          onClick={() => setActiveTab('phase3')}
        >
          <BadgeDollarSign size={15} />
          <span>3. Selling</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'agent' ? 'active' : ''}`}
          onClick={() => setActiveTab('agent')}
        >
          <Bot size={15} />
          <span>AI Explainer</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div className="tab-content-area">
        {loading && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#06b6d4' }}>
            Auditing statutory compliance against PostGIS & KMBR 2019...
          </div>
        )}

        {/* TAB 1: PHASE 1 (BUYING LAND) */}
        {!loading && activeTab === 'phase1' && p1Data && (
          <>
            <div className="info-section-card">
              <div className="section-title">
                <span>Title & Land Fitness Checks</span>
                <span className={`check-badge ${p1Data.overall === 'PASS' ? 'pass' : 'fail'}`}>
                  [{p1Data.overall}]
                </span>
              </div>

              {p1Data.checks?.map((c, i) => (
                <div key={i} className="check-item-row">
                  <span
                    className={`check-badge ${
                      c.verdict === 'PASS'
                        ? 'pass'
                        : c.verdict === 'WARN'
                        ? 'warn'
                        : 'fail'
                    }`}
                  >
                    [{c.verdict}]
                  </span>
                  <div style={{ flex: 1 }}>
                    <div className="check-title">
                      {c.check.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="check-detail">{c.detail}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Stamp Duty Calculator */}
            {p1Data.stamp_duty && (
              <div className="info-section-card">
                <div className="section-title">
                  <span>Stamp Duty & Registration Fee</span>
                  <Calculator size={16} color="#06b6d4" />
                </div>

                <div className="input-row-group">
                  <span className="input-label">Declared Consideration (₹):</span>
                  <input
                    type="number"
                    className="input-field"
                    value={declaredPrice}
                    onChange={(e) => setDeclaredPrice(Number(e.target.value))}
                  />
                  <button
                    onClick={recalculatePhase1}
                    className="chip-btn"
                    style={{ background: '#06b6d4', color: '#070b14', fontWeight: 700 }}
                  >
                    Recalc
                  </button>
                </div>

                <div className="metrics-keyval-grid" style={{ marginTop: '12px' }}>
                  <div className="kv-cell">
                    <div className="kv-label">Stamp Duty (8%)</div>
                    <div className="kv-value">
                      ₹{p1Data.stamp_duty.stamp_duty_inr?.toLocaleString('en-IN')}
                    </div>
                  </div>
                  <div className="kv-cell">
                    <div className="kv-label">Registration Fee (2%)</div>
                    <div className="kv-value">
                      ₹{p1Data.stamp_duty.registration_fee_inr?.toLocaleString('en-IN')}
                    </div>
                  </div>
                </div>
                <div
                  style={{
                    marginTop: '8px',
                    fontSize: '0.85rem',
                    color: '#38bdf8',
                    fontWeight: 700,
                  }}
                >
                  Total Government Fee: ₹
                  {p1Data.stamp_duty.total_fees_inr?.toLocaleString('en-IN')}
                </div>
              </div>
            )}
          </>
        )}

        {/* TAB 2: PHASE 2 (KMBR 2019 BUILDING RULES) */}
        {!loading && activeTab === 'phase2' && p2Data && (
          <>
            <div className="info-section-card">
              <div className="section-title">
                <span>Proposed Structure Parameters</span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                <div>
                  <div className="kv-label">Floors</div>
                  <input
                    type="number"
                    min="1"
                    max="15"
                    className="input-field"
                    style={{ width: '100%' }}
                    value={p2Floors}
                    onChange={(e) => setP2Floors(Number(e.target.value))}
                  />
                </div>
                <div>
                  <div className="kv-label">Height (m)</div>
                  <input
                    type="number"
                    step="0.5"
                    min="3"
                    className="input-field"
                    style={{ width: '100%' }}
                    value={p2Height}
                    onChange={(e) => setP2Height(Number(e.target.value))}
                  />
                </div>
                <div>
                  <div className="kv-label">Cost / m² (₹)</div>
                  <input
                    type="number"
                    className="input-field"
                    style={{ width: '100%' }}
                    value={p2CostSqm}
                    onChange={(e) => setP2CostSqm(Number(e.target.value))}
                  />
                </div>
              </div>
              <button
                onClick={recalculatePhase2}
                className="chip-btn"
                style={{
                  marginTop: '10px',
                  width: '100%',
                  background: '#06b6d4',
                  color: '#070b14',
                  fontWeight: 700,
                  padding: '6px',
                }}
              >
                Re-evaluate KMBR Clearances
              </button>
            </div>

            {/* Setback Measurements & Feasibility */}
            <div className="info-section-card">
              <div className="section-title">
                <span>KMBR 2019 Setback Clearances</span>
                <span className={`check-badge ${p2Data.overall === 'PASS' ? 'pass' : 'fail'}`}>
                  [{p2Data.overall}]
                </span>
              </div>

              {p2Data.checks
                ?.filter((c) => !['restricted_zones', 'demo_footprint_clipped'].includes(c.check))
                .map((c, i) => (
                  <div key={i} className="check-item-row">
                    <span
                      className={`check-badge ${
                        c.verdict === 'PASS'
                          ? 'pass'
                          : c.verdict === 'WARN'
                          ? 'warn'
                          : 'fail'
                      }`}
                    >
                      [{c.verdict}]
                    </span>
                    <div style={{ flex: 1 }}>
                      <div className="check-title">
                        {c.check.replace('_', ' ').toUpperCase()}
                      </div>
                      <div className="check-detail">{c.detail}</div>
                    </div>
                  </div>
                ))}

              {p2Data.measurements && (
                <div className="metrics-keyval-grid" style={{ marginTop: '12px' }}>
                  <div className="kv-cell">
                    <div className="kv-label">Plot Coverage</div>
                    <div className="kv-value">{p2Data.measurements.coverage_pct}%</div>
                  </div>
                  <div className="kv-cell">
                    <div className="kv-label">Floor Area Ratio (FAR)</div>
                    <div className="kv-value">{p2Data.measurements.far}</div>
                  </div>
                  <div className="kv-cell">
                    <div className="kv-label">Front Setback Clearance</div>
                    <div className="kv-value">{p2Data.measurements.front_m} m</div>
                  </div>
                  <div className="kv-cell">
                    <div className="kv-label">Rear Setback Clearance</div>
                    <div className="kv-value">{p2Data.measurements.rear_m} m</div>
                  </div>
                  <div className="kv-cell">
                    <div className="kv-label">Terrain Slope</div>
                    <div className="kv-value" style={{ color: p2Data.measurements.avg_slope_pct > 20 ? (p2Data.measurements.has_retaining_wall ? '#f59e0b' : '#f43f5e') : '#10b981' }}>
                      {p2Data.measurements.avg_slope_pct}%{' '}
                      <span style={{ fontSize: '0.7rem' }}>
                        {p2Data.measurements.avg_slope_pct > 20 ? (p2Data.measurements.has_retaining_wall ? '[Retaining Wall]' : '[> 20% Limit]') : '[<= 20% Pass]'}
                      </span>
                    </div>
                  </div>
                  <div className="kv-cell">
                    <div className="kv-label">Elevation (MSL)</div>
                    <div className="kv-value">
                      {p2Data.measurements.elevation_range_m ? `${p2Data.measurements.elevation_range_m[0]}m - ${p2Data.measurements.elevation_range_m[1]}m` : '18m - 22m'}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* BOCW Cess Card */}
            {p2Data.bocw_cess && (
              <div className="info-section-card">
                <div className="section-title">
                  <span>BOCW Construction Workers Cess</span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>
                  Total Built-up Area: <b>{p2Data.measurements?.builtup_area_sqm} m²</b>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#38bdf8', fontWeight: 700, marginTop: '4px' }}>
                  Welfare Cess (1%): ₹{p2Data.bocw_cess.cess_inr?.toLocaleString('en-IN')}
                </div>
              </div>
            )}
          </>
        )}

        {/* TAB 3: PHASE 3 (SELLING COMPLIANCE & TAXES) */}
        {!loading && activeTab === 'phase3' && p3Data && (
          <>
            <div className="info-section-card">
              <div className="section-title">
                <span>Municipal Assessment & OC Audit</span>
                <span className={`check-badge ${p3Data.overall === 'PASS' ? 'pass' : 'fail'}`}>
                  [{p3Data.overall}]
                </span>
              </div>

              {p3Data.checks?.map((c, i) => (
                <div key={i} className="check-item-row">
                  <span
                    className={`check-badge ${
                      c.verdict === 'PASS'
                        ? 'pass'
                        : c.verdict === 'WARN'
                        ? 'warn'
                        : 'fail'
                    }`}
                  >
                    [{c.verdict}]
                  </span>
                  <div style={{ flex: 1 }}>
                    <div className="check-title">
                      {c.check.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="check-detail">{c.detail}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Section 194-IA TDS & Capital Gains Interactive Form */}
            <div className="info-section-card">
              <div className="section-title">
                <span>Taxes on Property Transfer</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <div className="kv-label">Sale Consideration (₹)</div>
                  <input
                    type="number"
                    className="input-field"
                    style={{ width: '100%' }}
                    value={salePrice}
                    onChange={(e) => setSalePrice(Number(e.target.value))}
                  />
                </div>
                <div>
                  <div className="kv-label">Original Cost (₹)</div>
                  <input
                    type="number"
                    className="input-field"
                    style={{ width: '100%' }}
                    value={acqCost}
                    onChange={(e) => setAcqCost(Number(e.target.value))}
                  />
                </div>
              </div>

              <div style={{ marginTop: '8px' }}>
                <div className="kv-label">Acquisition Date</div>
                <input
                  type="date"
                  className="input-field"
                  style={{ width: '100%' }}
                  value={acqDate}
                  onChange={(e) => setAcqDate(e.target.value)}
                />
              </div>

              <button
                onClick={recalculatePhase3}
                className="chip-btn"
                style={{
                  marginTop: '10px',
                  width: '100%',
                  background: '#06b6d4',
                  color: '#070b14',
                  fontWeight: 700,
                  padding: '6px',
                }}
              >
                Recalculate 1% TDS & Capital Gains
              </button>

              {p3Data.tax_audits?.tds_194ia && (
                <div style={{ marginTop: '12px', padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Section 194-IA 1% TDS:</div>
                  <div style={{ fontSize: '0.9rem', color: '#f59e0b', fontWeight: 700 }}>
                    ₹{p3Data.tax_audits.tds_194ia.tds_amount_inr?.toLocaleString('en-IN')}{' '}
                    <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>
                      ({p3Data.tax_audits.tds_194ia.applicable ? 'Mandatory Form 26QB' : 'Exempt < ₹50L'})
                    </span>
                  </div>
                </div>
              )}

              {p3Data.tax_audits?.capital_gains && (
                <div style={{ marginTop: '8px', padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    Capital Gain Type ({p3Data.tax_audits.capital_gains.classification}):
                  </div>
                  <div style={{ fontSize: '0.9rem', color: '#10b981', fontWeight: 700 }}>
                    Est. Tax: ₹{p3Data.tax_audits.capital_gains.estimated_tax_inr?.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
                    Holding: {p3Data.tax_audits.capital_gains.holding_months} months •{' '}
                    {p3Data.tax_audits.capital_gains.section_54_eligible ? 'Eligible for Sec 54/54EC rollover' : 'No Sec 54 rollover (STCG)'}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {/* TAB 4: AI LEGAL EXPLAINER AGENT */}
        {activeTab === 'agent' && (
          <div className="ai-chat-container">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={16} color="#06b6d4" />
                <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>AI Legal Statutory Explainer</span>
              </div>
              <span className="ai-status-pill">KMBR 2019 Grounded</span>
            </div>

            <div className="quick-questions-strip">
              <button
                className="chip-btn"
                onClick={() => {
                  const q = `Can I construct a 2-storey house on Plot ${parcelId}? Check KMBR setbacks and coverage.`;
                  setAiQuery(q);
                  runAiQuery(q);
                }}
              >
                Can I build 2 floors?
              </button>
              <button
                className="chip-btn"
                onClick={() => {
                  const q = `Is Plot ${parcelId} legally safe to buy? Check encumbrance and wetland records.`;
                  setAiQuery(q);
                  runAiQuery(q);
                }}
              >
                Is it safe to buy?
              </button>
              <button
                className="chip-btn"
                onClick={() => {
                  const q = `What taxes, TDS, and municipal compliance apply if I sell Plot ${parcelId} for 75 Lakhs?`;
                  setAiQuery(q);
                  runAiQuery(q);
                }}
              >
                Taxes if sold for 75L?
              </button>
              <button
                className="chip-btn"
                onClick={() => {
                  const q = `Generate a full 3-phase due diligence report for Plot ${parcelId}.`;
                  setAiQuery(q);
                  runAiQuery(q);
                }}
              >
                Full 3-Phase Due Diligence
              </button>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
              <input
                type="text"
                className="input-field"
                style={{ flex: 1 }}
                placeholder="Ask any legal/building rule question..."
                value={aiQuery}
                onChange={(e) => setAiQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && runAiQuery()}
              />
              <button
                className="chip-btn"
                style={{ background: '#06b6d4', color: '#070b14', fontWeight: 700, padding: '0 12px' }}
                onClick={() => runAiQuery()}
                disabled={aiLoading}
              >
                Ask
              </button>
            </div>

            {aiLoading && (
              <div style={{ padding: '20px', textAlign: 'center', color: '#06b6d4', fontSize: '0.85rem' }}>
                Grounding explanation in PostGIS spatial metrics & gazetted regulation clauses...
              </div>
            )}

            {aiResponse && (
              <div className="ai-output-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.75rem', color: '#94a3b8' }}>
                  <span>Provider: <b>{aiResponse.llm_provider}</b></span>
                  <span>Verdict: <b style={{ color: aiResponse.overall_verdict === 'PASS' ? '#10b981' : '#f43f5e' }}>[{aiResponse.overall_verdict}]</b></span>
                </div>
                <div>{aiResponse.explanation}</div>

                {aiResponse.statutory_citations?.length > 0 && (
                  <div style={{ marginTop: '12px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '8px' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>
                      Statutory Citations:
                    </div>
                    {aiResponse.statutory_citations.map((c, i) => (
                      <div key={i} style={{ fontSize: '0.72rem', color: '#94a3b8', marginBottom: '2px' }}>
                        • <b>{c.doc_code || c.statute}</b> {c.clause_ref || c.section} (p. {c.page_no || 'N/A'})
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  );
}
