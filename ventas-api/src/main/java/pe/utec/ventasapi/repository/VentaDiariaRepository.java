package pe.utec.ventasapi.repository;

import java.time.LocalDate;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import pe.utec.ventasapi.model.VentaDiaria;

@Repository
public interface VentaDiariaRepository extends JpaRepository<VentaDiaria, Long>, JpaSpecificationExecutor<VentaDiaria> {

    List<VentaDiaria> findByProductoIdOrderByFechaDesc(Integer productoId);

    List<VentaDiaria> findByProductoIdAndFechaGreaterThanEqualOrderByFechaDesc(
            Integer productoId, LocalDate desde);
}
