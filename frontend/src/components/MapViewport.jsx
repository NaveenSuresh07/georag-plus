import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';

// Helper component to center and zoom map when a parcel is selected
function MapController({ selectedParcel, bounds }) {
  const map = useMap();

  useEffect(() => {
    if (selectedParcel && selectedParcel.geometry) {
      const geojsonLayer = L.geoJSON(selectedParcel);
      const parcelBounds = geojsonLayer.getBounds();
      if (parcelBounds.isValid()) {
        map.flyToBounds(parcelBounds, { maxZoom: 18, duration: 1.2, padding: [40, 40] });
      }
    }
  }, [selectedParcel, map]);

  useEffect(() => {
    if (bounds && bounds.length === 2 && !selectedParcel) {
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  }, [bounds, map, selectedParcel]);

  return null;
}

export default function MapViewport({
  parcelsGeojson,
  layersData,
  selectedParcelId,
  onSelectParcel,
  layerVisibility,
  onToggleLayer,
  studyAreaInfo,
}) {
  const geoJsonRef = useRef(null);

  // Parcel styling based on compliance status
  const getParcelStyle = (feature) => {
    const isSelected = feature.properties.parcel_id === selectedParcelId;
    const status = feature.properties.compliance_status;

    let fillColor = '#10b981'; // PASS
    let strokeColor = '#059669';

    if (status === 'WARN') {
      fillColor = '#f59e0b';
      strokeColor = '#d97706';
    } else if (status === 'FAIL') {
      fillColor = '#f43f5e';
      strokeColor = '#e11d48';
    }

    return {
      fillColor: fillColor,
      fillOpacity: isSelected ? 0.75 : 0.45,
      color: isSelected ? '#38bdf8' : strokeColor,
      weight: isSelected ? 3 : 1.2,
      dashArray: isSelected ? '' : '',
    };
  };

  // Attach hover and click interactions to each parcel
  const onEachParcel = (feature, layer) => {
    const props = feature.properties;
    const statusBadge =
      props.compliance_status === 'PASS'
        ? '<span style="color:#10b981;font-weight:700;">[PASS] COMPLIANT</span>'
        : props.compliance_status === 'WARN'
        ? '<span style="color:#f59e0b;font-weight:700;">[WARN] ATTENTION NEEDED</span>'
        : '<span style="color:#f43f5e;font-weight:700;">[FAIL] VIOLATION / RESTRICTION</span>';

    layer.bindTooltip(
      `
      <div style="font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.4; color: #f8fafc; padding: 4px;">
        <div style="font-weight: 700; font-size: 13px; color: #38bdf8;">Plot #${props.parcel_id} (Sy ${props.survey_no})</div>
        <div>Area: <b>${props.area_sqm} sq m</b> (${(props.area_sqm * 0.0247105).toFixed(2)} Cents)</div>
        <div>Status: ${statusBadge}</div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: 3px;">Click to inspect 3-phase compliance</div>
      </div>
      `,
      { sticky: true, className: 'custom-leaflet-tooltip' }
    );

    layer.on({
      click: () => {
        onSelectParcel(props.parcel_id);
      },
      mouseover: (e) => {
        const l = e.target;
        if (feature.properties.parcel_id !== selectedParcelId) {
          l.setStyle({ fillOpacity: 0.65, weight: 2, color: '#38bdf8' });
        }
      },
      mouseout: (e) => {
        const l = e.target;
        if (feature.properties.parcel_id !== selectedParcelId) {
          l.setStyle(getParcelStyle(feature));
        }
      },
    });
  };

  const center = studyAreaInfo?.center || [8.6953, 76.8146];
  const bounds = studyAreaInfo?.bounds;

  // Selected feature object for flyTo
  const selectedFeature = parcelsGeojson?.features?.find(
    (f) => f.properties.parcel_id === selectedParcelId
  );

  return (
    <div className="map-container-wrapper dark-tiles">
      <MapContainer
        center={center}
        zoom={16}
        scrollWheelZoom={true}
        className="leaflet-container"
      >
        <MapController selectedParcel={selectedFeature} bounds={bounds} />

        {/* Free Keyless OpenStreetMap Basemap with CSS Dark Filter */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />

        {/* 1. Buildings Footprints Layer */}
        {layerVisibility.buildings && layersData?.buildings && (
          <GeoJSON
            key="buildings-layer"
            data={layersData.buildings}
            style={() => ({
              fillColor: '#475569',
              fillOpacity: 0.4,
              color: '#334155',
              weight: 0.8,
            })}
          />
        )}

        {/* 2. Roads Layer */}
        {layerVisibility.roads && layersData?.roads && (
          <GeoJSON
            key="roads-layer"
            data={layersData.roads}
            style={(f) => ({
              color: f.properties.road_class === 'Secondary' ? '#818cf8' : '#64748b',
              weight: f.properties.road_class === 'Secondary' ? 3 : 1.8,
              opacity: 0.85,
            })}
          />
        )}

        {/* 3. Paddy Data Bank Wetlands */}
        {layerVisibility.paddy && layersData?.paddy_data_bank && (
          <GeoJSON
            key="paddy-layer"
            data={layersData.paddy_data_bank}
            style={() => ({
              fillColor: '#059669',
              fillOpacity: 0.45,
              color: '#10b981',
              weight: 2,
              dashArray: '4, 4',
            })}
          />
        )}

        {/* 4. Cadastral Parcels Layer */}
        {layerVisibility.parcels && parcelsGeojson && (
          <GeoJSON
            ref={geoJsonRef}
            key={`parcels-layer-${selectedParcelId}`}
            data={parcelsGeojson}
            style={getParcelStyle}
            onEachFeature={onEachParcel}
          />
        )}

        {/* 5. Utility Assets: Transformers (Point) and Water Mains (Line) */}
        {layerVisibility.utilities && layersData?.utility_assets && (
          <GeoJSON
            key="utility-layer"
            data={layersData.utility_assets}
            pointToLayer={(feature, latlng) => {
              // High voltage transformer marker
              return L.circleMarker(latlng, {
                radius: 6,
                fillColor: '#f59e0b',
                color: '#ffffff',
                weight: 1.5,
                opacity: 1,
                fillOpacity: 0.9,
              });
            }}
            style={(feature) => {
              if (feature.geometry.type === 'LineString') {
                return {
                  color: '#06b6d4',
                  weight: 2.5,
                  opacity: 0.8,
                  dashArray: '5, 5',
                };
              }
              return {};
            }}
          />
        )}
      </MapContainer>

      {/* Layer Toggle Floating Control */}
      <div className="layer-controls-overlay">
        <div className="layer-controls-title">Map Layers</div>
        <label className="layer-checkbox-row">
          <input
            type="checkbox"
            checked={layerVisibility.parcels}
            onChange={(e) =>
              onToggleLayer('parcels', e.target.checked)
            }
          />
          <span>Cadastral Parcels (534)</span>
        </label>
        <label className="layer-checkbox-row">
          <input
            type="checkbox"
            checked={layerVisibility.buildings}
            onChange={(e) =>
              onToggleLayer('buildings', e.target.checked)
            }
          />
          <span>Building Footprints</span>
        </label>
        <label className="layer-checkbox-row">
          <input
            type="checkbox"
            checked={layerVisibility.roads}
            onChange={(e) =>
              onToggleLayer('roads', e.target.checked)
            }
          />
          <span>Road Network</span>
        </label>
        <label className="layer-checkbox-row">
          <input
            type="checkbox"
            checked={layerVisibility.paddy}
            onChange={(e) =>
              onToggleLayer('paddy', e.target.checked)
            }
          />
          <span>Paddy Data Bank (Wetlands)</span>
        </label>
        <label className="layer-checkbox-row">
          <input
            type="checkbox"
            checked={layerVisibility.utilities}
            onChange={(e) =>
              onToggleLayer('utilities', e.target.checked)
            }
          />
          <span>Utilities (KSEB / KWA)</span>
        </label>
      </div>

      {/* Map Legend Overlay */}
      <div className="map-legend-overlay">
        <div className="legend-item">
          <div className="legend-badge" style={{ background: '#10b981' }} />
          <span>PASS: Clear Title & Conforming</span>
        </div>
        <div className="legend-item">
          <div className="legend-badge" style={{ background: '#f59e0b' }} />
          <span>WARN: Pending OC / Arrears / TDS</span>
        </div>
        <div className="legend-item">
          <div className="legend-badge" style={{ background: '#f43f5e' }} />
          <span>FAIL: Unauthorized / Wetland / Setback</span>
        </div>
      </div>
    </div>
  );
}
