/**
 * AudioEngine.js
 * 
 * Bu modül, React uygulamanızın "Ses Motoru"dur.
 * Tüm Tone.js ve Web Audio API işlemleri burada döner.
 * React bileşeniniz (UI) sadece buradaki fonksiyonları çağırır.
 * 
 * GEREKSİNİMLER:
 * npm install tone
 * (Opsiyonel: rubberband-web - TimeStretch WASM için)
 */

import * as Tone from "tone";

export class AudioEngine {
    constructor() {
        this.player = null;
        this.nodes = {}; // Efekt düğümlerini tutar
        this.chain = []; // Efekt zincir sırası
        this.stemUrl = "";

        // --- 1. Master Output ---
        this.masterGain = new Tone.Gain(1).toDestination();

        // --- 2. Efektleri Başlat (Bypass modunda) ---
        this.initializeEffects();
    }

    async init(stemUrl) {
        await Tone.start();
        this.stemUrl = stemUrl;

        // Player oluştur
        this.player = new Tone.Player(stemUrl).connect(this.nodes.inputGain);
        await Tone.loaded();
        console.log("AudioEngine: Hazır!");
    }

    play() { this.player?.start(); }
    stop() { this.player?.stop(); }

    /**
     * Tüm efektleri oluşturur ve zincire bağlar.
     * Sıralama: Input -> Dynamics -> EQ -> Mod -> Time -> Output
     */
    initializeEffects() {
        // --- A. GİRİŞ KONTROL ---
        this.nodes.inputGain = new Tone.Gain(1);

        // --- B. DİNAMİKLER ---
        this.nodes.compressor = new Tone.Compressor({ threshold: -24, ratio: 12, attack: 0.003, release: 0.25 });
        this.nodes.limiter = new Tone.Limiter(-1); // -1dB tavan
        this.nodes.noiseGate = new Tone.Gate(-40);

        // --- C. FİLTRELER (EQ) ---
        // Tone.js'de tek bir Filter node'u tip değiştirerek Lowpass/Highpass vb. olur.
        // Burada örnek olarak çoklu filtre zinciri kuruyoruz.
        this.nodes.lowpass = new Tone.Filter(20000, "lowpass");
        this.nodes.highpass = new Tone.Filter(0, "highpass");
        this.nodes.bandpass = new Tone.Filter(1000, "bandpass"); // Q değeri ile aralık belirlenir
        this.nodes.notch = new Tone.Filter(1000, "notch");
        this.nodes.peak = new Tone.Filter(1000, "peaking");
        this.nodes.lowshelf = new Tone.Filter(200, "lowshelf");
        this.nodes.highshelf = new Tone.Filter(2000, "highshelf");

        // --- D. MODÜLASYON & DISTORTION ---
        this.nodes.chorus = new Tone.Chorus(4, 2.5, 0.5).start(); // start() gerekir LFO için
        this.nodes.phaser = new Tone.Phaser({ frequency: 15, octaves: 5, baseFrequency: 1000 });
        this.nodes.distortion = new Tone.Distortion(0);
        this.nodes.bitcrusher = new Tone.BitCrusher(16); // 16 bit (temiz), 4 bit (kirli)
        this.nodes.chebyshev = new Tone.Chebyshev(1); // 1 = etkisiz, 100 = hard clip

        // --- E. MEKAN & ZAMAN (Time & Space) ---
        this.nodes.delay = new Tone.FeedbackDelay("8n", 0); // DelayTime, Feedback
        this.nodes.reverb = new Tone.Reverb({ decay: 1.5, preDelay: 0.01 });
        this.nodes.reverb.wet.value = 0; // Başlangıçta kapalı
        // Convolution için özel dosya yüklenmeli, şimdilik standart Reverb yeterli değilse eklenir.

        // --- F. PITCH & UTILS ---
        this.nodes.pitchShift = new Tone.PitchShift(0);
        this.nodes.panner = new Tone.Panner(0); // -1 sol, +1 sağ

        // --- ZİNCİRLEME (CHAIN) ---
        // Sinyal bu sırayla akar:
        this.nodes.inputGain
            .connect(this.nodes.noiseGate)
            .connect(this.nodes.compressor)
            .connect(this.nodes.distortion)
            .connect(this.nodes.bitcrusher)
            .connect(this.nodes.chebyshev)
            .connect(this.nodes.lowpass)
            .connect(this.nodes.highpass)
            .connect(this.nodes.bandpass)
            .connect(this.nodes.notch)
            .connect(this.nodes.peak)
            .connect(this.nodes.lowshelf)
            .connect(this.nodes.highshelf)
            .connect(this.nodes.phaser)
            .connect(this.nodes.chorus)
            .connect(this.nodes.pitchShift)
            .connect(this.nodes.delay)
            .connect(this.nodes.reverb)
            .connect(this.nodes.panner)
            .connect(this.nodes.limiter)
            .connect(this.masterGain);

        // Not: Bandpass/Notch vb. çoğu zaman bypass (devre dışı) olmalı, Tone.js'de mix=0 yoksa frekans uçlarına çekilir.
        // Veya "dry/wet" mantığı Gain node'ları ile kurulur. Tone.js efektlerinin çoğunda .wet özelliği vardır.
        // Filtreler için: frekansı insan kulağının duymadığı yere çekerek (bypass) etkisi yaratılır.
    }

    // ==========================================================
    // UI KONTROL METODLARI (React Burayı Çağıracak)
    // ==========================================================

    /**
     * Reverb Miktarını Ayarlar
     * @param {number} value - 0.0 (Kuru) ile 1.0 (Tam Islak)
     */
    setReverb(value) {
        this.nodes.reverb.wet.value = value;
    }

    /**
     * Delay Ayarları
     * @param {number} feedback - 0.0 - 0.9
     * @param {number} wet - 0.0 - 1.0
     */
    setDelay(feedback, wet) {
        this.nodes.delay.feedback.value = feedback;
        this.nodes.delay.wet.value = wet;
    }

    /**
     * Distortion Miktarı
     * @param {number} amount - 0.0 - 1.0
     */
    setDistortion(amount) {
        this.nodes.distortion.distortion = amount;
        // Tone.Distortion wet/dry default 1'dir, mix bozulabilir, wet ayarı da yapılabilir.
        this.nodes.distortion.wet.value = amount > 0 ? 1 : 0;
    }

    /**
     * Lowpass Filtre (Basları geçir)
     * @param {number} freq - 20Hz - 20000Hz (20000 = Etkisiz)
     */
    setLowpass(freq) {
        this.nodes.lowpass.frequency.value = freq;
    }

    // ... Diğer tüm set fonksiyonları benzer mantıkla eklenir ...

    // ==========================================================
    // TIME STRETCH (BPM) - RUBBERBAND WASM
    // ==========================================================

    /**
     * Rubberband WASM Motorunu Hazırlar.
     * Bu fonksiyon React uygulamanız başladığında (init) çağrılmalıdır.
     * GEREKSİNİM: 'rubberband-processor.js' ve 'rubberband.wasm' dosyaları public klasöründe olmalıdır.
     */
    async initRubberband() {
        try {
            // AudioWorklet modülünü yükle (Dosya yolu projenize göre değişebilir)
            await Tone.context.audioWorklet.addModule("/rubberband-processor.js");

            // Rubberband Node'unu oluştur
            this.nodes.timeStretcher = new AudioWorkletNode(Tone.context.rawContext, 'rubberband-processor');

            // Parametreleri ayarla (Default: 1.0 hız, 1.0 pitch)
            this.nodes.timeStretcher.parameters.get('pitch').value = 1.0;
            this.nodes.timeStretcher.parameters.get('tempo').value = 1.0;

            console.log("Rubberband WASM yüklendi.");

            // Eğer Rubberband kullanacaksak, Player'ı direkt ona bağlamalıyız
            // Player -> TimeStretcher -> InputGain -> ...
            if (this.player) {
                this.player.disconnect();
                this.player.connect(this.nodes.timeStretcher);
                this.nodes.timeStretcher.connect(this.nodes.inputGain);
            }

        } catch (e) {
            console.error("KRİTİK HATA: Rubberband WASM yüklenemedi! Time Stretch çalışmayacak.", e);
            console.error("Lütfen 'rubberband-processor.js' ve 'rubberband.wasm' dosyalarının public klasöründe olduğundan emin olun.");
            this.nodes.timeStretcher = null;
            // Fallback YOK. Kullanıcı özellikle bunu istedi.
        }
    }

    /**
     * BPM Değişimi (Time Stretch)
     * @param {number} ratio - 1.0 = Normal, 1.2 = %20 Hızlı
     */
    setPlaybackRate(ratio) {
        if (this.nodes.timeStretcher) {
            // PRO YÖNTEM: Rubberband WASM (Pitch bozulmadan hız değişir)
            const tempoParam = this.nodes.timeStretcher.parameters.get('tempo');
            if (tempoParam) {
                tempoParam.value = ratio;
            }
        } else {
            console.warn("Rubberband yüklü değil, Hız değişimi yapılmadı.");
        }
    }

    /**
     * Pitch Shift (Sadece Pitch değişir, Hız aynı kalır - Rubberband ile)
     * @param {number} ratio - 1.0 = Normal, 2.0 = 1 oktav tiz
     */
    setPitch(ratio) {
        if (this.nodes.timeStretcher) {
            const pitchParam = this.nodes.timeStretcher.parameters.get('pitch');
            if (pitchParam) {
                pitchParam.value = ratio;
            }
        } else {
            console.warn("Rubberband yüklü değil, Pitch değişimi yapılmadı.");
        }
    }

    // ==========================================================
    // BACKEND EXPORT (JSON OLUŞTURMA)
    // ==========================================================

    /**
     * O anki ayarları Python Backend'in anlayacağı JSON formatına çevirir.
     * Bu çıktıyı POST /process-audio 'ya gönderirsiniz.
     * @returns {Array} Effect Chain JSON
     */
    getExportJSON() {
        const chain = [];

        // 1. Dynamics
        // Compressor her zaman aktif gibi düşünülebilir veya wet>0 ise eklenir
        if (this.nodes.compressor.threshold.value < 0) {
            chain.push({
                name: "Compressor",
                params: {
                    threshold_db: this.nodes.compressor.threshold.value,
                    ratio: this.nodes.compressor.ratio.value,
                    attack_ms: this.nodes.compressor.attack.value * 1000,
                    release_ms: this.nodes.compressor.release.value * 1000
                }
            });
        }

        // Gain
        // Master Gain
        if (this.masterGain.gain.value !== 1) {
            chain.push({
                name: "Gain",
                params: { gain_db: 20 * Math.log10(this.masterGain.gain.value) } // Linear -> dB
            });
        }

        // 2. Filters
        if (this.nodes.lowpass.frequency.value < 20000) {
            chain.push({
                name: "LowpassFilter",
                params: { cutoff_hz: this.nodes.lowpass.frequency.value }
            });
        }

        // 3. Effects
        if (this.nodes.distortion.distortion > 0) {
            chain.push({
                name: "Distortion",
                params: { drive_db: this.nodes.distortion.distortion * 20 } // Tahmini map
            });
        }

        if (this.nodes.reverb.wet.value > 0) {
            chain.push({
                name: "Reverb",
                params: {
                    room_size: 0.5, // Tone.js decay ile tam mapleşmez, yaklaşık değer
                    wet_level: this.nodes.reverb.wet.value,
                    dry_level: 1 - this.nodes.reverb.wet.value
                }
            });
        }

        if (this.nodes.delay.wet.value > 0) {
            chain.push({
                name: "Delay",
                params: {
                    delay_seconds: parseFloat(this.nodes.delay.delayTime.value), // Notation '8n' ise saniyeye çevrilmeli
                    feedback: this.nodes.delay.feedback.value,
                    mix: this.nodes.delay.wet.value
                }
            });
        }

        // ... Diğer tüm efektler için IF kontrolleri ile ekleme yapılır

        return chain;
    }
}
