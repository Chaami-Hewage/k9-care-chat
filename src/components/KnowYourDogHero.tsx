import { Canvas, useFrame, useLoader, useThree } from "@react-three/fiber";
import { ContactShadows } from "@react-three/drei";
import { a, useSpring } from "@react-spring/three";
import { motion } from "framer-motion";
import { Suspense, useEffect, useRef, useState } from "react";
import * as THREE from "three";

import heroDog from "@/assets/hero-chibi-dog.png";

const LOOK_CONFIG = { mass: 1.15, tension: 88, friction: 22 };
const PLAY_CONFIG = { mass: 0.7, tension: 260, friction: 16 };
const SETTLE_CONFIG = { mass: 1.1, tension: 110, friction: 18 };

function DogFigure({ textureUrl }: { textureUrl: string }) {
  const texture = useLoader(THREE.TextureLoader, textureUrl);
  const floatGroup = useRef<THREE.Group>(null);
  const playing = useRef(false);
  const { pointer, clock, gl } = useThree();
  const lastPointer = useRef({ x: 0, y: 0 });
  const idleBlend = useRef(1);

  const [spring, api] = useSpring(() => ({
    rotX: 0,
    rotY: 0,
    rotZ: 0,
    jumpY: 0,
    squash: 1,
    config: LOOK_CONFIG,
  }));

  useEffect(() => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 8;
    texture.needsUpdate = true;
  }, [texture]);

  useFrame(() => {
    const t = clock.getElapsedTime();
    const moved =
      Math.abs(pointer.x - lastPointer.current.x) + Math.abs(pointer.y - lastPointer.current.y);
    lastPointer.current = { x: pointer.x, y: pointer.y };
    idleBlend.current = THREE.MathUtils.lerp(idleBlend.current, moved > 0.002 ? 0 : 1, 0.04);

    if (!playing.current) {
      api.start({
        rotX: -pointer.y * 0.42,
        rotY: pointer.x * 0.62,
        config: LOOK_CONFIG,
      });
    }

    if (floatGroup.current) {
      const floatY = Math.sin(t * 0.75) * 0.11 * idleBlend.current;
      const bob = 1 + Math.sin(t * 0.95) * 0.022 * idleBlend.current;
      floatGroup.current.position.y = floatY;
      floatGroup.current.scale.setScalar(bob);
    }
  });

  const playHappy = () => {
    if (playing.current) return;
    playing.current = true;
    gl.domElement.style.cursor = "pointer";

    void api.start({
      to: async (next) => {
        await next({ jumpY: 0.08, squash: 0.92, rotZ: 0, config: PLAY_CONFIG });
        await next({
          jumpY: 0.72,
          squash: 1.08,
          rotZ: Math.PI * 2,
          rotX: -0.18,
          rotY: 0.12,
          config: PLAY_CONFIG,
        });
        await next({
          jumpY: 0,
          squash: 1,
          rotX: 0,
          rotY: 0,
          rotZ: Math.PI * 2,
          config: SETTLE_CONFIG,
        });
        api.set({ rotZ: 0 });
        playing.current = false;
      },
    });
  };

  return (
    <a.group
      onClick={playHappy}
      onPointerOver={() => {
        gl.domElement.style.cursor = "pointer";
      }}
      onPointerOut={() => {
        gl.domElement.style.cursor = "auto";
      }}
      position-y={spring.jumpY}
      rotation-x={spring.rotX}
      rotation-y={spring.rotY}
      rotation-z={spring.rotZ}
      scale={spring.squash}
    >
      <group ref={floatGroup}>
        <mesh castShadow>
          <planeGeometry args={[2.55, 2.55]} />
          <meshPhysicalMaterial
            map={texture}
            transparent
            alphaTest={0.12}
            roughness={0.35}
            metalness={0.04}
            clearcoat={0.55}
            clearcoatRoughness={0.28}
            side={THREE.DoubleSide}
          />
        </mesh>
      </group>
    </a.group>
  );
}

function Scene() {
  return (
    <>
      <ambientLight intensity={0.78} />
      <directionalLight
        position={[3.4, 5.2, 4.2]}
        intensity={1.35}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <directionalLight position={[-3.2, 1.4, -2]} intensity={0.45} color="#c4b5fd" />
      <pointLight position={[0, -0.4, 2.2]} intensity={0.55} color="#fda4af" />
      <DogFigure textureUrl={heroDog} />
      <ContactShadows
        position={[0, -1.28, 0]}
        opacity={0.32}
        scale={6}
        blur={2.4}
        far={3.2}
      />
    </>
  );
}

export function KnowYourDogHero() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <section className="relative overflow-hidden rounded-[2rem] bg-card/35 shadow-xl shadow-brand/10 ring-1 ring-card/60 backdrop-blur-2xl">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_70%_40%,rgba(255,255,255,0.55),transparent_55%)]" />
      <div className="grid items-center gap-2 lg:grid-cols-[1.05fr_1fr]">
        <div className="relative z-10 px-6 py-8 sm:px-10 sm:py-12">
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
            className="text-xs font-semibold uppercase tracking-[0.22em] text-brand"
          >
            Know Your Dog
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
            className="font-display mt-3 max-w-md text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl"
          >
            A soft little pal that follows your cursor.
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.16, ease: [0.22, 1, 0.36, 1] }}
            className="mt-4 max-w-md text-sm leading-relaxed text-ink/65 sm:text-base"
          >
            Move around — they look with you. Click for a happy flip. Then chat with Dr. Paws about
            vaccines, symptoms, and everyday care.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.24 }}
            className="mt-6 flex flex-wrap gap-2 text-xs font-medium text-ink/55"
          >
            <span className="rounded-full bg-card/70 px-3 py-1.5 ring-1 ring-card/80">3D look-at</span>
            <span className="rounded-full bg-card/70 px-3 py-1.5 ring-1 ring-card/80">Springy motion</span>
            <span className="rounded-full bg-card/70 px-3 py-1.5 ring-1 ring-card/80">Click to play</span>
          </motion.div>
        </div>

        <div className="relative h-[320px] w-full sm:h-[400px] lg:h-[460px]">
          {mounted ? (
            <Canvas
              shadows
              dpr={[1, 1.75]}
              gl={{ alpha: true, antialias: true }}
              camera={{ position: [0, 0.15, 3.55], fov: 38 }}
              className="h-full w-full touch-none"
            >
              <Suspense fallback={null}>
                <Scene />
              </Suspense>
            </Canvas>
          ) : (
            <div className="flex h-full items-center justify-center">
              <img
                src={heroDog}
                alt="Cute chibi dog mascot"
                className="h-[78%] w-auto object-contain drop-shadow-xl"
              />
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
