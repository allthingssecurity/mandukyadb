import React from 'react';
import {AbsoluteFill} from 'remotion';

const Box: React.FC<{title: string; desc: string}> = ({title, desc}) => (
  <div style={{background: '#131a33', border: '1px solid #263154', borderRadius: 12, padding: 16}}>
    <div style={{fontWeight: 700, fontSize: 22, marginBottom: 6}}>{title}</div>
    <div style={{opacity: 0.9, fontSize: 18}}>{desc}</div>
  </div>
);

export const ArchSlide: React.FC = () => {
  return (
    <AbsoluteFill style={{padding: 80}}>
      <div style={{fontSize: 42, fontWeight: 800, marginBottom: 24}}>Architecture: Four States</div>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16}}>
        <Box title="Jagrat (Storage)" desc="File-backed tables; schemas and rows persisted to disk."/>
        <Box title="Swapna (Planner)" desc="Parses SQL; basic planning / normalization."/>
        <Box title="Sushupti (Cache)" desc="In-memory caches for hot data and results."/>
        <Box title="Turiya (Execution)" desc="Executes statements; coordinates storage + caching."/>
      </div>
    </AbsoluteFill>
  );
};

