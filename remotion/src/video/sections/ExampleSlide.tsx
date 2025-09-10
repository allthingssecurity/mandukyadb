import React, {useMemo} from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, interpolate} from 'remotion';
import type {ExampleStep} from '../MandukyaVideo';

const Panel: React.FC<{label: string; children: React.ReactNode}> = ({label, children}) => (
  <div style={{background: '#0f1730', border: '1px solid #263154', borderRadius: 12, padding: 16}}>
    <div style={{fontWeight: 700, fontSize: 18, marginBottom: 8, opacity: 0.9}}>{label}</div>
    <div style={{fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace', fontSize: 18, whiteSpace: 'pre-wrap', lineHeight: 1.45}}>
      {children}
    </div>
  </div>
);

const fmtResult = (r: any) => {
  if (typeof r === 'string') return r;
  if (Array.isArray(r)) return r.map((row) => JSON.stringify(row)).join('\n');
  if (r == null) return '';
  return JSON.stringify(r, null, 2);
};

export const ExampleSlide: React.FC<{steps: ExampleStep[]}> = ({steps}) => {
  const frame = useCurrentFrame();
  const per = Math.floor(600 / Math.max(1, steps.length));
  const visibleCount = Math.min(steps.length, Math.floor(frame / per) + 1);
  const subset = useMemo(() => steps.slice(0, visibleCount), [visibleCount, steps]);

  return (
    <AbsoluteFill style={{padding: 60}}>
      <div style={{fontSize: 38, fontWeight: 800, marginBottom: 12}}>Examples</div>
      <div style={{opacity: 0.85, marginBottom: 24}}>Running SQL and showing live outputs captured from Python.</div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 18}}>
        {subset.map((s, i) => {
          const localStart = i * per;
          const y = interpolate(Math.max(0, frame - localStart), [0, 10], [30, 0], {extrapolateRight: 'clamp'});
          const op = interpolate(Math.max(0, frame - localStart), [0, 10], [0, 1], {extrapolateRight: 'clamp'});
          return (
            <div key={i} style={{transform: `translateY(${y}px)`, opacity: op}}>
              <div style={{fontWeight: 700, marginBottom: 10, fontSize: 22}}>{s.title}</div>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12}}>
                <Panel label="SQL">
                  {s.sql || '(API call)'}
                </Panel>
                <Panel label="Output">
                  {fmtResult(s.result)}
                </Panel>
              </div>
              {typeof s.elapsed_ms === 'number' && (
                <div style={{marginTop: 6, fontSize: 14, opacity: 0.6}}>Elapsed: {s.elapsed_ms?.toFixed(2)} ms</div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

