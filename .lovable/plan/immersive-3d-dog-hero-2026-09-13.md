# Immersive 3D dog hero

## What will change
- Replace the current flat mascot motion with a full-width, transparent 3D canvas that remains integrated with the existing breed-photo background.
- Build the mascot from layered transparent image planes so it gains visible depth, soft lighting, floor shadow, and pointer-responsive perspective without requiring a separate 3D model file.
- Make the dog smoothly turn toward the pointer using frame-by-frame spring motion, with gentle idle floating and scale breathing when untouched.
- Add a click interaction that triggers a playful jump and roll, then settles naturally back into the pointer-following pose.
- Keep the chat, dog profile, breed switching, and vet request behavior unchanged.
- Respect reduced-motion preferences and provide a lightweight non-WebGL fallback.

## Technical details
- Add React Three Fiber, Drei, and Three.js.
- Keep the canvas client-only so server rendering remains stable.
- Use `useFrame` with damped spring targets for pointer tracking and animation state.
- Use transparent texture layers, contact shadows, and restrained lighting for a dimensional cutout treatment.
- Verify rendering, pointer tracking, click animation, fallback behavior, and layout at desktop and mobile sizes.
