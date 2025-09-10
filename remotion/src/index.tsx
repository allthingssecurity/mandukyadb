import {Composition, Folder, registerRoot} from 'remotion';
import {MandukyaVideo, VIDEO_DURATION, VIDEO_FPS, VIDEO_HEIGHT, VIDEO_WIDTH} from './video/MandukyaVideo';
import examples from '../data/examples.json' assert { type: 'json' };

registerRoot(() => {
  return (
    <>
      <Folder name="MandukyaDB">
        <Composition
          id="MandukyaVideo"
          component={MandukyaVideo}
          durationInFrames={VIDEO_DURATION}
          fps={VIDEO_FPS}
          width={VIDEO_WIDTH}
          height={VIDEO_HEIGHT}
          defaultProps={{examples}}
        />
      </Folder>
    </>
  );
});

